"""E3-2 ChatBI 双路由 + 行列权限契约测试 — 明细兜底 DSL（列裁剪/行过滤/拒绝审计）"""
import sqlite3

import pytest

from semantic_layer import SemanticGuardError, SemanticLayer

_MDL = None


@pytest.fixture(scope="module")
def layer():
    return SemanticLayer.load(_mdl_path())


def _mdl_path():
    from pathlib import Path
    return Path(__file__).resolve().parents[2] / "mdl" / "demo.mdl.yaml"


@pytest.fixture()
def target_db(tmp_path):
    path = str(tmp_path / "target.db")
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE users (user_id INTEGER PRIMARY KEY, name TEXT, city TEXT, created_at TEXT)")
    conn.execute("CREATE TABLE events (event_id INTEGER PRIMARY KEY, user_id INTEGER, event_type TEXT, created_at TEXT)")
    conn.execute("INSERT INTO users VALUES (1,'张三','上海','2026-09-01')")
    conn.execute("INSERT INTO users VALUES (2,'李四','北京','2026-09-15')")
    conn.execute("INSERT INTO users VALUES (3,'王五','上海','2026-10-01')")
    for i, uid in enumerate((1, 1, 2, 3), start=1):
        conn.execute("INSERT INTO events VALUES (?,?, 'login', ?)", (i, uid, "2026-10-15"))
    conn.commit()
    conn.close()
    return path


class TestGrants:
    def test_agent_explicit_grant_prunes_columns(self, layer):
        grant = layer._grant_for("bole", "users")
        assert grant["columns"] == ["user_id", "city"]

    def test_unlisted_agent_inherits_full(self, layer):
        grant = layer._grant_for("tianshu", "users")
        assert set(grant["columns"]) == {"user_id", "name", "city", "created_at"}


class TestDetailQuery:
    def test_full_columns_for_unlisted_agent(self, layer, target_db):
        conn = sqlite3.connect(target_db)
        try:
            result = layer.detail_query(conn, "tianshu", {"table": "users", "limit": 10})
        finally:
            conn.close()
        assert result["row_count"] == 3
        assert result["columns"][0] == "user_id"

    def test_column_pruning_for_explicit_grant(self, layer, target_db):
        conn = sqlite3.connect(target_db)
        try:
            result = layer.detail_query(conn, "bole", {"table": "users", "limit": 10})
        finally:
            conn.close()
        assert result["row_count"] == 3
        assert all(set(row) == {"user_id", "city"} for row in result["rows"])

    def test_column_denied_for_explicit_grant_agent(self, layer, target_db):
        conn = sqlite3.connect(target_db)
        try:
            with pytest.raises(SemanticGuardError) as ei:
                layer.detail_query(conn, "bole", {"table": "users",
                                                  "columns": ["user_id", "name"]})
        finally:
            conn.close()
        assert ei.value.code == "COLUMN_DENIED"

    def test_filter_column_denied(self, layer, target_db):
        conn = sqlite3.connect(target_db)
        try:
            with pytest.raises(SemanticGuardError) as ei:
                layer.detail_query(conn, "bole", {"table": "users",
                                                  "filters": {"name": "张三"}})
        finally:
            conn.close()
        assert ei.value.code == "FILTER_COLUMN_DENIED"

    def test_filter_applied_in_memory(self, layer, target_db):
        conn = sqlite3.connect(target_db)
        try:
            result = layer.detail_query(conn, "tianshu", {
                "table": "users", "filters": {"city": "上海"}, "limit": 10})
        finally:
            conn.close()
        assert result["row_count"] == 2
        assert all(row["city"] == "上海" for row in result["rows"])

    def test_unknown_table_rejected(self, layer, target_db):
        conn = sqlite3.connect(target_db)
        try:
            with pytest.raises(SemanticGuardError) as ei:
                layer.detail_query(conn, "tianshu", {"table": "secret_table"})
        finally:
            conn.close()
        assert ei.value.code == "TABLE_NOT_ALLOWED"

    def test_row_cap_enforced(self, layer, target_db):
        conn = sqlite3.connect(target_db)
        try:
            with pytest.raises(SemanticGuardError) as ei:
                layer.detail_query(conn, "tianshu", {"table": "users", "limit": 2})
        finally:
            conn.close()
        assert ei.value.code == "ROW_LIMIT_EXCEEDED"


class TestDualRoute:
    def test_metric_first_then_detail_fallback(self, layer, target_db):
        """双路由语义：指标问答优先命中 → 明细兜底按需走结构化 DSL"""
        metric = layer.match_metric("注册用户总数是多少")
        assert metric == "total_users"
        conn = sqlite3.connect(target_db)
        try:
            metric_result = layer.execute_metric(conn, metric)
            detail = layer.detail_query(conn, "tianshu", {
                "table": "users", "filters": {"city": "上海"}, "limit": 10})
        finally:
            conn.close()
        assert metric_result["rows"][0][0] == 3
        assert detail["row_count"] == 2
