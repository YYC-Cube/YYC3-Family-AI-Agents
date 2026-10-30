#!/usr/bin/env python3
"""E2-3 分层记忆 · Semantic 层首批 — Mem0 式事实记忆（SQLite 自包含）

分层定位：Semantic 层（事实记忆）；Working/Episodic/Procedural 列入后续批次。
三步管线（Mem0 式）：
  1) 抽取：规则 MVP（身份/偏好/归属/事实声明四类模式，可解释零依赖）；LLM 抽取为环境钩子后续
  2) 去重合并：同 (agent, 归一化事实) 命中即合并（hits+1、置信度上调 0.05 封顶 1.0），不新增行
  3) 置信度衰减：读取时按天指数衰减（半衰期 30 天），低于阈值沉睡不删（可追溯）

治理中枢独有卖点：增/改/删全量入审计链（audit_cb=auditor.record）。
本模块不反向依赖 governance_hub：连接与审计回调由调用方注入。
全部 SQL 为单行参数化查询（? 占位符）。
"""
import math
import re
import sqlite3
from datetime import datetime, timezone

HALF_LIFE_DAYS = 30.0
MIN_CONFIDENCE = 0.30
NEW_FACT_CONFIDENCE = 0.6
MERGE_CONFIDENCE_STEP = 0.1

# 事实抽取规则 MVP（身份 / 偏好 / 归属 / 事实声明）——备选项最长优先，避免短匹配吞掉长语义
_EXTRACT_RULES = [
    re.compile(r"(?:我|我们)(?:是|叫做|名叫|名为|是)\s*([^。；\n，,]{1,20})"),
    re.compile(r"(?:我|我们)?(?:偏好使用|喜欢|偏好|倾向于)\s*([^。；\n]{1,40})"),
    re.compile(r"(?:我|我们)(?:属于|来自|任职于|服务于)\s*([^。；\n，,]{1,30})"),
    re.compile(r"([^\s。；\n，,]{1,20}(?:项目|系统|平台))(?:是|处于|已进入)([^。；\n]{1,50})"),
]

_SCHEMA = """
CREATE TABLE IF NOT EXISTS semantic_memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent TEXT NOT NULL,
    fact TEXT NOT NULL,
    fact_norm TEXT NOT NULL,
    source TEXT NOT NULL DEFAULT 'rule',
    confidence REAL NOT NULL DEFAULT 1.0,
    hits INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    forgotten INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_sem_agent ON semantic_memory(agent, forgotten);
"""


def ensure_table(conn: sqlite3.Connection) -> None:
    conn.executescript(_SCHEMA)
    conn.commit()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_fact(fact: str) -> str:
    return re.sub(r"[\s。；，,、!？?.'\"()（）]+", "", (fact or "")).lower()


def extract_facts(text: str) -> list:
    """规则抽取 MVP：返回去重后的事实列表（保序）。"""
    facts = []
    for pattern in _EXTRACT_RULES:
        for m in pattern.finditer(text or ""):
            groups = [g.strip() for g in m.groups() if g and g.strip()]
            fact = " ".join(groups) if len(groups) > 1 else groups[0]
            fact = fact.strip()
            if fact and fact not in facts:
                facts.append(fact)
    return facts


def keyword_overlap(query: str, fact: str) -> float:
    """MVP 相关度：query 中的 2-gram 在 fact 中的覆盖率（0..1）。零依赖、可解释。"""
    q = normalize_fact(query)
    f = normalize_fact(fact)
    if not q or not f:
        return 0.0
    grams = {q[i:i + 2] for i in range(len(q) - 1)} or {q}
    hit = sum(1 for g in grams if g in f)
    return hit / len(grams)


def store(conn: sqlite3.Connection, agent: str, text: str, *,
          source: str = "rule", correlation_id: str = "", audit_cb=None) -> list:
    """抽取并存储：新事实入库（audit memory_store），重复事实合并（audit memory_update）。"""
    ensure_table(conn)
    results = []
    now = _now()
    for fact in extract_facts(text):
        norm = normalize_fact(fact)
        row = conn.execute(
            "SELECT id, hits, confidence FROM semantic_memory WHERE agent=? AND fact_norm=? AND forgotten=0",
            (agent, norm)).fetchone()
        if row:
            fid, hits, conf = row
            new_conf = min(1.0, conf + MERGE_CONFIDENCE_STEP)
            conn.execute(
                "UPDATE semantic_memory SET hits=?, confidence=?, updated_at=? WHERE id=?",
                (hits + 1, new_conf, now, fid))
            # 先提交再审计：审计回调使用独立连接，事务未提交会锁库（busy_timeout 耗尽）
            conn.commit()
            results.append({"id": fid, "fact": fact, "action": "merged",
                            "confidence": new_conf, "hits": hits + 1})
            if audit_cb:
                audit_cb("governance_hub", "memory_update",
                         {"fact_id": fid, "agent": agent, "hits": hits + 1,
                          "confidence": new_conf}, correlation_id)
        else:
            cur = conn.execute(
                "INSERT INTO semantic_memory(agent, fact, fact_norm, source, confidence, hits, created_at, updated_at, forgotten) VALUES (?,?,?,?,?,1,?,?,0)",
                (agent, fact, norm, source, NEW_FACT_CONFIDENCE, now, now))
            conn.commit()
            results.append({"id": cur.lastrowid, "fact": fact, "action": "stored",
                            "confidence": NEW_FACT_CONFIDENCE, "hits": 1})
            if audit_cb:
                audit_cb("governance_hub", "memory_store",
                         {"fact_id": cur.lastrowid, "agent": agent, "fact": fact[:60]},
                         correlation_id)
    return results


def recall(conn: sqlite3.Connection, agent: str, query: str, top_k: int = 5,
           min_confidence: float = MIN_CONFIDENCE) -> list:
    """召回：关键词覆盖度 × 时间衰减置信度排序；数字不匹配重罚（近重复事实精度）；
    低于阈值沉睡（不删，可追溯）。"""
    ensure_table(conn)
    rows = conn.execute(
        "SELECT id, fact, confidence, hits, created_at, updated_at FROM semantic_memory WHERE agent=? AND forgotten=0",
        (agent,)).fetchall()
    now = datetime.now(timezone.utc)
    query_digits = set(re.findall(r"\d+", query or ""))
    scored = []
    for fid, fact, conf, hits, created, updated in rows:
        ts = datetime.fromisoformat(updated)
        age_days = max(0.0, (now - ts).total_seconds() / 86400)
        effective = conf * math.pow(0.5, age_days / HALF_LIFE_DAYS)
        if effective < min_confidence:
            continue
        overlap = keyword_overlap(query, fact)
        if overlap <= 0:
            continue
        # 数字不匹配重罚：查询中的编号在事实中缺失 → 近重复事实降权（精度）
        fact_digits = set(re.findall(r"\d+", fact))
        if query_digits and not query_digits.issubset(fact_digits):
            overlap *= 0.2
        scored.append({"id": fid, "fact": fact, "hits": hits,
                       "confidence": conf, "effective_confidence": round(effective, 4),
                       "score": round(overlap * effective, 4)})
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:max(1, top_k)]


def forget(conn: sqlite3.Connection, agent: str, fact_id: int, *,
           correlation_id: str = "", audit_cb=None) -> dict:
    """软删除（forgotten=1）：召回不再可见，行保留可追溯。audit memory_forget。"""
    ensure_table(conn)
    cur = conn.execute(
        "UPDATE semantic_memory SET forgotten=1, updated_at=? WHERE id=? AND agent=? AND forgotten=0",
        (_now(), int(fact_id), agent))
    conn.commit()
    forgotten = cur.rowcount > 0
    if forgotten and audit_cb:
        audit_cb("governance_hub", "memory_forget",
                 {"fact_id": int(fact_id), "agent": agent}, correlation_id)
    return {"fact_id": int(fact_id), "forgotten": forgotten}


def list_active(conn: sqlite3.Connection, agent: str, limit: int = 100) -> list:
    ensure_table(conn)
    rows = conn.execute(
        "SELECT id, fact, source, confidence, hits, created_at, updated_at FROM semantic_memory WHERE agent=? AND forgotten=0 ORDER BY updated_at DESC LIMIT ?",
        (agent, int(limit))).fetchall()
    return [{"id": r[0], "fact": r[1], "source": r[2], "confidence": r[3],
             "hits": r[4], "created_at": r[5], "updated_at": r[6]} for r in rows]
