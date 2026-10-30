"""E3-4 学习闭环契约测试 — usage 回填 / golden 候选学习 / 指标版本晋升回滚门控（全量入审计链）"""
import json
import sqlite3

import learning_loop
import pytest
from governance_hub import init_db


@pytest.fixture()
def gov_client(gov_db):
    return gov_db.app.test_client()


@pytest.fixture()
def conn(gov_db):
    conn = gov_db.connect_db()
    learning_loop.ensure_tables(conn)
    yield conn
    conn.close()


@pytest.fixture(autouse=True)
def _clean_learning(conn):
    yield
    conn.execute("DELETE FROM metric_versions")
    conn.execute("DELETE FROM golden_candidates")
    conn.commit()


class TestUsageInsights:
    def test_aggregates_by_agent_and_model(self, conn):
        now = learning_loop._now()
        for prompt, comp in ((10, 5), (20, 8)):
            conn.execute("INSERT INTO token_usage(agent, prompt_tokens, completion_tokens, total_tokens, latency_ms, model, timestamp) VALUES (?,?,?,?,?,?,?)",
                         ("tianshu", prompt, comp, prompt + comp, 120.0, "Qwen/3.6", now))
        conn.execute("INSERT INTO token_usage(agent, prompt_tokens, completion_tokens, total_tokens, latency_ms, model, timestamp) VALUES (?,?,?,?,?,?,?)",
                     ("lingyun", 7, 3, 10, 80.0, "Qwen/3.6", now))
        conn.commit()
        insights = learning_loop.usage_insights(conn, hours=24)
        by_agent = {a["agent"]: a for a in insights["by_agent"]}
        assert by_agent["tianshu"]["calls"] == 2
        assert by_agent["tianshu"]["prompt_tokens"] == 30
        assert by_agent["lingyun"]["calls"] == 1
        assert insights["by_model"][0]["model"] == "Qwen/3.6"


class TestGoldenCandidates:
    def test_failed_questions_become_candidates(self, gov_client, conn):
        gov_client.post("/semantic/query", json={
            "question": "量子纠缠的实验设计", "correlation_id": "learn-1"})
        candidates = learning_loop.golden_candidates_from_events(conn, limit=20)
        assert any(c["question"] == "量子纠缠的实验设计" for c in candidates)
        assert all(c["source"] == "learned" for c in candidates)

    def test_successful_queries_not_candidates(self, gov_client, conn, monkeypatch, tmp_path):
        monkeypatch.setenv("YYC3_SEMANTIC_TARGET_DB", str(tmp_path / "t.db"))
        t = sqlite3.connect(str(tmp_path / "t.db"))
        t.execute("CREATE TABLE users (user_id INTEGER PRIMARY KEY, name TEXT, city TEXT, created_at TEXT)")
        t.commit()
        t.close()
        gov_client.post("/semantic/query", json={
            "question": "注册用户总数是多少", "correlation_id": "learn-2"})
        candidates = [c for c in learning_loop.golden_candidates_from_events(conn, limit=50)
                      if c["question"] == "注册用户总数是多少"]
        assert candidates == [], "成功匹配的指标问答不入候选"

    def test_adopt_writes_audit(self, gov_client):
        adopt = gov_client.post("/learning/golden-adopt", json={
            "question": "如何评估数据质量成熟度", "correlation_id": "adopt-1"})
        assert adopt.status_code == 200 and adopt.get_json()["adopted"] is True
        trail = gov_client.get("/audit/trail?limit=50").get_json()
        assert any(e.get("action") == "golden_candidate_adopted" for e in trail)


class TestMetricVersionGating:
    def test_promote_below_threshold_rejected(self, conn):
        learning_loop.ensure_metric_version(conn, "total_users", "1.0.0")
        result = learning_loop.promote_metric(conn, "total_users", 0.5)
        assert result["action"] == "promote_rejected"
        assert result["version"] == "1.0.0"

    def test_promote_above_threshold_bumps_minor(self, conn):
        learning_loop.ensure_metric_version(conn, "total_users", "1.0.0")
        result = learning_loop.promote_metric(conn, "total_users", 0.95)
        assert result["action"] == "promoted"
        assert result["from_version"] == "1.0.0" and result["version"] == "1.1.0"

    def test_rollback_patches_down_with_floor(self, conn):
        learning_loop.ensure_metric_version(conn, "total_users", "1.0.0")
        r1 = learning_loop.rollback_metric(conn, "total_users")
        assert r1["action"] == "rolled_back" and r1["version"] == "1.0.0", "1.0.0 为回滚地板"


class TestHubLearningEndpoints:
    def test_metric_version_endpoints_gate(self, gov_client):
        below = gov_client.post("/learning/metric-promote", json={
            "metric": "total_users", "eval_pass_rate": 0.5}).get_json()
        assert below["action"] == "promote_rejected"
        above = gov_client.post("/learning/metric-promote", json={
            "metric": "total_users", "eval_pass_rate": 0.95}).get_json()
        assert above["action"] == "promoted" and above["version"] == "1.1.0"
        rolled = gov_client.post("/learning/metric-rollback", json={
            "metric": "total_users", "eval_pass_rate": 0.0}).get_json()
        assert rolled["action"] == "rolled_back" and rolled["version"] == "1.0.0"
        trail = gov_client.get("/audit/trail?limit=50").get_json()
        actions = [e.get("action") for e in trail]
        assert "metric_version_promoted" in actions and "metric_version_rolled_back" in actions

    def test_usage_insights_endpoint(self, gov_client):
        r = gov_client.get("/learning/usage-insights?hours=24").get_json()
        assert r["status"] == "ok" and "by_agent" in r and "by_model" in r
