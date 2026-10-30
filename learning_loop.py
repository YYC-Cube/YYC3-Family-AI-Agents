#!/usr/bin/env python3
"""E3-4 学习闭环 MVP — usage 回填 / golden 候选生成 / 指标版本晋升与回滚门控

闭环三段（对齐规划文档 E3-4）：
  1) usage 回填：聚合 token_usage（按 agent/模型/时间窗）为学习洞察，供评估侧重与预算校准
  2) golden 候选扩充：从审计事件提取语义查询失败（blocked / 未匹配指标）的真实问题，
     生成 golden 候选（source=learned，采纳为部署侧评审动作）
  3) 指标版本门控：METRIC_VERSIONS 状态表（SQLite）——评估通过率 ≥ PROMOTE_THRESHOLD
     才允许次版本 +1（晋升）；人工判定可回退 patch 版本（回滚）；全部入审计链

治理中枢独有卖点：候选生成 / 版本晋升 / 回滚全部入审计链。
本模块不反向依赖 governance_hub：连接与审计回调由调用方注入；全部 SQL 单行参数化。
"""
import json
import sqlite3
from datetime import datetime, timedelta, timezone

PROMOTE_THRESHOLD = 0.9
ROLLBACK_THRESHOLD = 0.5

_SCHEMA = """
CREATE TABLE IF NOT EXISTS metric_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric TEXT NOT NULL,
    version TEXT NOT NULL,
    eval_pass_rate REAL NOT NULL DEFAULT 0,
    updated_at TEXT NOT NULL,
    UNIQUE(metric, version)
);
CREATE TABLE IF NOT EXISTS golden_candidates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT NOT NULL,
    agent TEXT NOT NULL DEFAULT '',
    reason TEXT NOT NULL DEFAULT '',
    source TEXT NOT NULL DEFAULT 'learned',
    adopted INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL
);
"""


def ensure_tables(conn: sqlite3.Connection) -> None:
    conn.executescript(_SCHEMA)
    conn.commit()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _hours_ago(hours: int) -> str:
    return (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()


# ---------- 1) usage 回填 ----------

def usage_insights(conn: sqlite3.Connection, hours: int = 24) -> dict:
    """聚合 token_usage 为学习洞察（按 agent 汇总用量/延迟，按模型汇总分布）。"""
    rows = conn.execute(
        "SELECT agent, COUNT(*) AS calls, SUM(prompt_tokens) AS prompt_tokens, SUM(completion_tokens) AS completion_tokens, ROUND(AVG(latency_ms), 1) AS avg_latency_ms FROM token_usage WHERE timestamp >= ? GROUP BY agent ORDER BY calls DESC",
        (_hours_ago(hours),)).fetchall()
    by_agent = [{"agent": r[0], "calls": r[1], "prompt_tokens": r[2] or 0,
                 "completion_tokens": r[3] or 0, "avg_latency_ms": r[4]} for r in rows]
    model_rows = conn.execute(
        "SELECT model, COUNT(*) AS calls FROM token_usage WHERE timestamp >= ? GROUP BY model ORDER BY calls DESC",
        (_hours_ago(hours),)).fetchall()
    return {"window_hours": hours, "generated_at": _now(),
            "by_agent": by_agent,
            "by_model": [{"model": r[0] or "(unknown)", "calls": r[1]} for r in model_rows]}


# ---------- 2) golden 候选（从审计事件学习） ----------

def golden_candidates_from_events(conn: sqlite3.Connection, limit: int = 20) -> list:
    """扫描审计事件中的语义查询失败（blocked / 未匹配指标），去重生成 golden 候选。只读，不写审计。"""
    rows = conn.execute(
        "SELECT action, details, correlation_id, timestamp FROM behavior_events WHERE action IN ('semantic_query_blocked', 'semantic_query_no_match', 'semantic_query') ORDER BY id DESC LIMIT ?",
        (int(limit) * 4,)).fetchall()
    seen = set()
    candidates = []
    for action, details_text, cid, ts in rows:
        try:
            details = json.loads(details_text or "{}")
        except ValueError:
            continue
        question = details.get("question", "")
        if len(question) < 4 or question in seen:
            continue
        seen.add(question)
        if action == "semantic_query" and details.get("metric"):
            continue  # 成功匹配的指标问答不入候选
        reason = details.get("code", "") or ("no_match" if action.endswith("no_match") else "blocked")
        candidates.append({"question": question, "agent": "", "reason": reason,
                           "source": "learned", "correlation_id": cid, "timestamp": ts})
        if len(candidates) >= limit:
            break
    return candidates


def adopt_candidate(conn: sqlite3.Connection, question: str, agent: str = "",
                    correlation_id: str = "", audit_cb=None) -> dict:
    """采纳 golden 候选：写入 golden_candidates（adopted=1）并审计。"""
    ensure_tables(conn)
    cur = conn.execute(
        "INSERT INTO golden_candidates(question, agent, reason, source, adopted, created_at) VALUES (?,?,?,?,1,?)",
        (question, agent, "learned", "learned", _now()))
    conn.commit()
    if audit_cb:
        audit_cb("governance_hub", "golden_candidate_adopted",
                 {"candidate_id": cur.lastrowid, "question": question[:80]}, correlation_id)
    return {"candidate_id": cur.lastrowid, "question": question, "adopted": True}


# ---------- 3) 指标版本门控（晋升 / 回滚） ----------

def ensure_metric_version(conn: sqlite3.Connection, metric: str, version: str = "1.0.0",
                          eval_pass_rate: float = 0.0, audit_cb=None,
                          correlation_id: str = "") -> None:
    ensure_tables(conn)
    cur = conn.execute(
        "INSERT OR IGNORE INTO metric_versions(metric, version, eval_pass_rate, updated_at) VALUES (?,?,?,?)",
        (metric, version, eval_pass_rate, _now()))
    conn.commit()
    if cur.rowcount and audit_cb:
        audit_cb("governance_hub", "metric_version_initialized",
                 {"metric": metric, "version": version}, correlation_id)


def current_metric_version(conn: sqlite3.Connection, metric: str) -> dict:
    row = conn.execute(
        "SELECT version, eval_pass_rate, updated_at FROM metric_versions WHERE metric=? ORDER BY updated_at DESC LIMIT 1",
        (metric,)).fetchone()
    if not row:
        return {"metric": metric, "version": None, "eval_pass_rate": None}
    return {"metric": metric, "version": row[0], "eval_pass_rate": row[1], "updated_at": row[2]}


def _bump_minor(version: str) -> str:
    major, minor, _patch = version.split(".")
    return f"{major}.{int(minor) + 1}.0"


def _down(version: str) -> str:
    major, minor, patch = version.split(".")
    patch_num = int(patch)
    return f"{major}.{minor}.{patch_num - 1}" if patch_num > 0 else version


def promote_metric(conn: sqlite3.Connection, metric: str, eval_pass_rate: float, *,
                   correlation_id: str = "", audit_cb=None) -> dict:
    """评估通过率 ≥ PROMOTE_THRESHOLD → 晋升次版本号（能力增强语义）；
    否则拒绝晋升（保持当前版本，审计记录拒绝原因）。"""
    ensure_tables(conn)
    ensure_metric_version(conn, metric, audit_cb=audit_cb, correlation_id=correlation_id)
    current = current_metric_version(conn, metric)
    version = current.get("version") or "1.0.0"
    if eval_pass_rate < PROMOTE_THRESHOLD:
        result = {"metric": metric, "action": "promote_rejected",
                  "eval_pass_rate": eval_pass_rate, "threshold": PROMOTE_THRESHOLD,
                  "version": version}
        if audit_cb:
            audit_cb("governance_hub", "metric_promote_rejected",
                     {**result, "reason": "pass_rate_below_threshold"}, correlation_id)
        return result
    new_version = _bump_minor(version)
    conn.execute(
        "INSERT OR REPLACE INTO metric_versions(metric, version, eval_pass_rate, updated_at) VALUES (?,?,?,?)",
        (metric, new_version, eval_pass_rate, _now()))
    conn.commit()
    result = {"metric": metric, "action": "promoted",
              "from_version": version, "version": new_version,
              "eval_pass_rate": eval_pass_rate}
    if audit_cb:
        audit_cb("governance_hub", "metric_version_promoted",
                 {"metric": metric, "from": version, "to": new_version,
                  "eval_pass_rate": eval_pass_rate}, correlation_id)
    return result


def rollback_metric(conn: sqlite3.Connection, metric: str, eval_pass_rate: float = 0.0, *,
                    correlation_id: str = "", audit_cb=None) -> dict:
    """人工判定回退：回退到该指标历史上一版本（无历史则保持地板）。审计 metric_version_rolled_back。"""
    ensure_tables(conn)
    ensure_metric_version(conn, metric, audit_cb=audit_cb, correlation_id=correlation_id)
    current = current_metric_version(conn, metric)
    version = current.get("version") or "1.0.0"
    prev = conn.execute(
        "SELECT version FROM metric_versions WHERE metric=? AND version<>? ORDER BY updated_at DESC, id DESC LIMIT 1",
        (metric, version)).fetchone()
    new_version = (prev[0] if prev else _down(version)) or version
    conn.execute(
        "INSERT OR REPLACE INTO metric_versions(metric, version, eval_pass_rate, updated_at) VALUES (?,?,?,?)",
        (metric, new_version, eval_pass_rate, _now()))
    conn.commit()
    result = {"metric": metric, "action": "rolled_back",
              "from_version": version, "version": new_version,
              "eval_pass_rate": eval_pass_rate}
    if audit_cb:
        audit_cb("governance_hub", "metric_version_rolled_back",
                 {"metric": metric, "from": version, "to": new_version}, correlation_id)
    return result
