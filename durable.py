#!/usr/bin/env python3
"""E3-3 持久化执行 MVP — 步骤级 checkpoint（SQLite）+ correlation_id 断点恢复

设计：
- 步骤粒度：对话管线的关键阶段（context_injection / llm_inference）完成后即落 checkpoint
- 恢复语义：同一 correlation_id + 同一请求指纹（fingerprint）重入时，已 done 的步骤直接
  复用其产物（如 LLM 回答），不再重复执行；指纹不同视为新运行
- 自包含 SQLite（默认 ./data/durable.db，YYC3_DURABLE_DB 可覆盖）；运行时产物不入库
- 与语义缓存互补：缓存按内容指纹（TTL 短），checkpoint 按 cid+请求指纹（跨 TTL 长存）
- 全部 SQL 为单行参数化查询（? 占位符）；写入前先 SELECT 判存再 UPDATE/INSERT

MVP 边界：仅覆盖非流式 /chat 管线两步；流式与更多步骤列入 E3-3 后续批次。
"""
import hashlib
import json
import os
import sqlite3
from datetime import datetime, timezone

DB_PATH = os.environ.get(
    "YYC3_DURABLE_DB",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "durable.db"))

_SCHEMA = """
CREATE TABLE IF NOT EXISTS durable_steps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    correlation_id TEXT NOT NULL,
    fingerprint TEXT NOT NULL,
    step TEXT NOT NULL,
    status TEXT NOT NULL,
    payload TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE(correlation_id, fingerprint, step)
);
"""


def connect(db_path: str = None) -> sqlite3.Connection:
    path = db_path or DB_PATH
    os.makedirs(os.path.dirname(path), exist_ok=True)
    conn = sqlite3.connect(path, timeout=10)
    conn.executescript(_SCHEMA)
    conn.commit()
    return conn


def fingerprint(payload: dict) -> str:
    """请求指纹：影响生成结果的最小字段集的规范化哈希（不含 correlation_id）。"""
    blob = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def record_step(conn: sqlite3.Connection, correlation_id: str, fingerprint: str,
                step: str, status: str, payload: dict) -> None:
    """步骤完成即落 checkpoint（已存在则覆盖为最新，保留首次 created_at）。"""
    now = _now()
    payload_text = json.dumps(payload, ensure_ascii=False)
    row = conn.execute(
        "SELECT id FROM durable_steps WHERE correlation_id=? AND fingerprint=? AND step=?",
        (correlation_id, fingerprint, step)).fetchone()
    if row:
        conn.execute(
            "UPDATE durable_steps SET status=?, payload=?, updated_at=? WHERE id=?",
            (status, payload_text, now, row[0]))
    else:
        conn.execute(
            "INSERT INTO durable_steps(correlation_id, fingerprint, step, status, payload, created_at, updated_at) VALUES (?,?,?,?,?,?,?)",
            (correlation_id, fingerprint, step, status, payload_text, now, now))
    conn.commit()


def get_step(conn: sqlite3.Connection, correlation_id: str, fingerprint: str,
             step: str, status: str = "done") -> dict:
    """读取已完成步骤的产物；入参仅作查询条件（参数化），返回 JSON 载荷或 None。"""
    row = conn.execute(
        "SELECT payload FROM durable_steps WHERE correlation_id=? AND fingerprint=? AND step=? AND status=?",
        (correlation_id, fingerprint, step, status)).fetchone()
    if not row:
        return None
    try:
        return json.loads(row[0])
    except ValueError:
        return None
