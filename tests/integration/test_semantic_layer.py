"""E3-1 大数据语义层契约测试 — MDL 解析 / 治理管线 / 指标执行 / hub 端点（审计闭环）"""
import json
import sqlite3

import pytest

import semantic_layer
from semantic_layer import SemanticGuardError, SemanticLayer

REPO = None  # 由 conftest 隐式保证 cwd 无关：MDL 路径经 REPO 常量注入
import os
from pathlib import Path

_MDL = Path(__file__).resolve().parents[2] / "mdl" / "demo.mdl.yaml"


@pytest.fixture()
def gov_client(gov_db):
    return gov_db.app.test_client()


@pytest.fixture(scope="module")
def layer():
    layer = SemanticLayer.load(_MDL)
    layer.check_registry_drift()
    return layer


@pytest.fixture()
def target_db(tmp_path):
    """种子目标库：users 3 行 + events 505 行（超出 row_limit=500 用于超限用例）"""
    path = str(tmp_path / "target.db")
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE users (user_id INTEGER PRIMARY KEY, name TEXT, city TEXT, created_at TEXT)")
    conn.execute("CREATE TABLE events (event_id INTEGER PRIMARY KEY, user_id INTEGER, event_type TEXT, created_at TEXT)")
    for i in range(1, 4):
        conn.execute("INSERT INTO users VALUES (?,?,?,?)", (i, f"用户{i}", "上海", "2026-10-01"))
    for i in range(1, 506):
        conn.execute("INSERT INTO events VALUES (?,?,?,?)", (i, 1, "login", "2026-10-15"))
    conn.commit()
    conn.close()
    return path


class TestMdlParse:
    def test_load_demo_mdl(self, layer):
        assert layer.mdl["name"] == "yyc3-demo"
        assert set(layer.tables) == {"users", "events"}
        assert layer.row_limit == 500

    def test_registry_drift_clean(self, layer):
        layer.check_registry_drift()  # 不抛即通过

    def test_registry_drift_detected(self):
        bad = {"version": "1.0", "name": "x", "dialect": "sqlite",
               "tables": [{"name": "other", "columns": []}], "metrics": []}
        with pytest.raises(SemanticGuardError) as ei:
            SemanticLayer(bad).check_registry_drift.__func__(SemanticLayer(bad))
        # check_registry_drift 依赖 self.tables —— 直接用抛错路径验证
        layer = SemanticLayer(bad)
        with pytest.raises(SemanticGuardError):
            layer.check_registry_drift()


class TestValidateSql:
    def test_select_appends_limit(self, layer):
        assert layer.validate_sql("SELECT * FROM users") == "SELECT * FROM users LIMIT 500"

    def test_leading_drop_hits_select_guard(self, layer):
        with pytest.raises(SemanticGuardError) as ei:
            layer.validate_sql("DROP TABLE users")
        assert ei.value.code == "SQL_NOT_SELECT"

    def test_rejects_forbidden_keyword_embedded(self, layer):
        with pytest.raises(SemanticGuardError) as ei:
            layer.validate_sql("SELECT load_extension('x') FROM users")
        assert ei.value.code == "SQL_FORBIDDEN_KEYWORD"

    def test_rejects_multi_statement(self, layer):
        with pytest.raises(SemanticGuardError) as ei:
            layer.validate_sql("SELECT * FROM users; DROP TABLE users")
        assert ei.value.code == "SQL_MULTI_STATEMENT"

    def test_rejects_unknown_table(self, layer):
        with pytest.raises(SemanticGuardError) as ei:
            layer.validate_sql("SELECT * FROM secret_table")
        assert ei.value.code == "TABLE_NOT_ALLOWED"

    def test_rejects_over_limit(self, layer):
        with pytest.raises(SemanticGuardError) as ei:
            layer.validate_sql("SELECT * FROM users LIMIT 10000")
        assert ei.value.code == "LIMIT_EXCEEDED"

    def test_rejects_non_select(self, layer):
        with pytest.raises(SemanticGuardError) as ei:
            layer.validate_sql("UPDATE users SET name = 'x'")
        assert ei.value.code == "SQL_NOT_SELECT"


class TestMetricExecution:
    def test_match_total_users(self, layer, target_db):
        metric = layer.match_metric("目前一共有多少注册用户？")
        assert metric == "total_users"
        conn = sqlite3.connect(target_db)
        try:
            result = layer.execute_metric(conn, metric)
        finally:
            conn.close()
        assert result["row_count"] == 1 and result["rows"][0][0] == 3

    def test_metric_not_found(self, layer, target_db):
        conn = sqlite3.connect(target_db)
        try:
            with pytest.raises(SemanticGuardError) as ei:
                layer.execute_metric(conn, "nonexistent")
        finally:
            conn.close()
        assert ei.value.code == "METRIC_NOT_FOUND"

    def test_context_prompt_contains_schema(self, layer):
        prompt = layer.context_prompt("有多少用户？")
        assert "users" in prompt and "events" in prompt and "total_users" in prompt


class TestHubEndpoints:
    @pytest.fixture(autouse=True)
    def _target_env(self, tmp_path, monkeypatch):
        path = str(tmp_path / "target.db")
        conn = sqlite3.connect(path)
        conn.execute("CREATE TABLE users (user_id INTEGER PRIMARY KEY, name TEXT, city TEXT, created_at TEXT)")
        conn.execute("CREATE TABLE events (event_id INTEGER PRIMARY KEY, user_id INTEGER, event_type TEXT, created_at TEXT)")
        for i in range(1, 4):
            conn.execute("INSERT INTO users VALUES (?,?,?,?)", (i, f"用户{i}", "上海", "2026-10-01"))
        conn.commit()
        conn.close()
        monkeypatch.setenv("YYC3_SEMANTIC_TARGET_DB", path)
        # 语义层单例已可能被其他用例加载；MDL 相同，无碍
        yield {"target": path}

    def test_mdl_endpoint(self, gov_client):
        r = gov_client.get("/semantic/mdl").get_json()
        assert r["status"] == "ok" and r["name"] == "yyc3-demo"
        assert set(r["metrics"]) == {"total_users", "active_users", "events_total"}

    def test_query_roundtrip_and_audit(self, gov_client):
        r = gov_client.post("/semantic/query", json={
            "question": "注册用户总数是多少", "correlation_id": "sem-q-1"})
        assert r.status_code == 200
        body = r.get_json()
        assert body["metric"] == "total_users" and body["row_count"] == 1
        trail = gov_client.get("/audit/trail?limit=50").get_json()
        assert any(e.get("action") == "semantic_query" for e in trail)

    def test_query_requires_question(self, gov_client):
        assert gov_client.post("/semantic/query", json={}).status_code == 400

    def test_query_no_metric_matched_422(self, gov_client):
        r = gov_client.post("/semantic/query", json={"question": "量子纠缠的实验设计"})
        assert r.status_code == 422
        assert r.get_json()["code"] == "NO_METRIC_MATCHED"
