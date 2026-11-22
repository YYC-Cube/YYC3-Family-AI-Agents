#!/usr/bin/env python3
"""E3-1 基线路径执行器：validate_sql 门禁后的 LLM SELECT 于一次性内存副本执行。

C 层只读（stdlib sqlite3 authorizer）：INSERT/UPDATE/DELETE/DROP/ALTER/ATTACH 等一切
写动作在引擎层被拒；副本随查询销毁，主数据零接触。独立模块使执行 sink 与实验编排分离，
便于单测与后续替换（Postgres 基线执行器同构）。"""

import sqlite3


def _readonly_authorizer(action, arg1, arg2, db_name, source):
    if action in (sqlite3.SQLITE_SELECT, sqlite3.SQLITE_READ, sqlite3.SQLITE_FUNCTION,
                  sqlite3.SQLITE_RECURSIVE):
        return sqlite3.SQLITE_OK
    return sqlite3.SQLITE_DENY


def safe_replica_read(main_conn, sql):
    """先经 validate_sql 门禁（调用方负责），再于副本以 authorizer 执行；返回行列表。"""
    replica = sqlite3.connect(":memory:")
    main_conn.backup(replica)
    replica.set_authorizer(_readonly_authorizer)
    try:
        return [list(r) for r in replica.execute(sql).fetchall()]
    finally:
        replica.close()
