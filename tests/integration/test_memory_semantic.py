"""E2-3 分层记忆 Semantic 层契约测试 — 抽取/去重合并/衰减召回/软删除/审计闭环 + 规模往返"""
import sqlite3

import memory_semantic
import pytest
from governance_hub import init_db


def _fresh_conn(tmp_path):
    conn = sqlite3.connect(str(tmp_path / "sem.db"))
    memory_semantic.ensure_table(conn)
    return conn


AUDIT = []


def _audit(agent, action, details, correlation_id=""):
    AUDIT.append({"agent": agent, "action": action,
                  "details": details, "correlation_id": correlation_id})


@pytest.fixture(autouse=True)
def _clean_audit():
    AUDIT.clear()
    yield
    AUDIT.clear()


@pytest.fixture()
def gov_client(gov_db):
    return gov_db.app.test_client()


class TestExtraction:
    def test_identity_fact(self):
        facts = memory_semantic.extract_facts("我是元启天枢团队的负责人")
        assert facts and any("负责人" in f or "元启天枢" in f for f in facts)

    def test_preference_fact(self):
        facts = memory_semantic.extract_facts("我偏好使用中文语言回答问题")
        assert facts and any("中文" in f for f in facts)

    def test_affiliation_fact(self):
        facts = memory_semantic.extract_facts("我们来自 YanYuCloudCube 团队")
        assert facts and any("YanYuCloudCube" in f for f in facts)

    def test_no_facts_returns_empty(self):
        assert memory_semantic.extract_facts("今天天气如何？") == []


class TestStoreDedupe:
    def test_store_and_merge(self, tmp_path):
        conn = _fresh_conn(tmp_path)
        r1 = memory_semantic.store(conn, "tianshu", "我偏好使用中文语言回答问题", audit_cb=_audit)
        r2 = memory_semantic.store(conn, "tianshu", "我偏好使用中文语言回答问题", audit_cb=_audit)
        assert r1[0]["action"] == "stored" and r2[0]["action"] == "merged"
        assert r2[0]["hits"] == 2
        assert r1[0]["confidence"] == pytest.approx(0.6)
        assert r2[0]["confidence"] == pytest.approx(0.7)
        rows = memory_semantic.list_active(conn, "tianshu")
        assert len(rows) == 1, "去重合并不得新增行"
        actions = [a["action"] for a in AUDIT]
        assert actions == ["memory_store", "memory_update"], "增/改双事件入审计链"

    def test_multi_agent_isolated(self, tmp_path):
        conn = _fresh_conn(tmp_path)
        memory_semantic.store(conn, "tianshu", "我偏好使用中文语言回答问题", audit_cb=_audit)
        rows = memory_semantic.list_active(conn, "lingyun")
        assert rows == []


class TestRecallDecay:
    def test_recall_keyword_ranking(self, tmp_path):
        conn = _fresh_conn(tmp_path)
        memory_semantic.store(conn, "tianshu", "我偏好使用中文语言回答问题", audit_cb=_audit)
        memory_semantic.store(conn, "tianshu", "我们来自 YanYuCloudCube 团队", audit_cb=_audit)
        results = memory_semantic.recall(conn, "tianshu", "语言偏好", top_k=5)
        assert results and "中文" in results[0]["fact"]
        assert results[0]["effective_confidence"] <= results[0]["confidence"]

    def test_decay_sleeps_below_threshold(self, tmp_path):
        conn = _fresh_conn(tmp_path)
        memory_semantic.store(conn, "tianshu", "我偏好使用中文语言回答问题", audit_cb=_audit)
        # 回溯 3 个半衰期：有效置信度 ≈ 1/8，仍高于 0.30 边界附近 → 直接推 4 个半衰期确保沉睡
        old = "2020-01-01T00:00:00+00:00"
        conn.execute("UPDATE semantic_memory SET updated_at=?", (old,))
        conn.commit()
        assert memory_semantic.recall(conn, "tianshu", "语言偏好") == [], "超龄事实应沉睡"
        rows = memory_semantic.list_active(conn, "tianshu")
        assert len(rows) == 1, "沉睡不删除（行保留可追溯）"

    def test_unrelated_query_no_match(self, tmp_path):
        conn = _fresh_conn(tmp_path)
        memory_semantic.store(conn, "tianshu", "我偏好使用中文语言回答问题", audit_cb=_audit)
        assert memory_semantic.recall(conn, "tianshu", "量子物理实验") == []


class TestForget:
    def test_forget_soft_deletes_and_audits(self, tmp_path):
        conn = _fresh_conn(tmp_path)
        stored = memory_semantic.store(conn, "tianshu", "我偏好使用中文语言回答问题", audit_cb=_audit)
        fid = stored[0]["id"]
        result = memory_semantic.forget(conn, "tianshu", fid, audit_cb=_audit)
        assert result["forgotten"] is True
        assert memory_semantic.recall(conn, "tianshu", "语言偏好") == []
        assert memory_semantic.list_active(conn, "tianshu") == []
        assert [a["action"] for a in AUDIT if a["action"] == "memory_forget"]
        # 软删除：行仍在库中可追溯
        row = conn.execute("SELECT forgotten FROM semantic_memory WHERE id=?", (fid,)).fetchone()
        assert row[0] == 1

    def test_forget_twice_is_idempotent_false(self, tmp_path):
        conn = _fresh_conn(tmp_path)
        stored = memory_semantic.store(conn, "tianshu", "我偏好使用中文语言回答问题", audit_cb=_audit)
        assert memory_semantic.forget(conn, "tianshu", stored[0]["id"])["forgotten"] is True
        assert memory_semantic.forget(conn, "tianshu", stored[0]["id"])["forgotten"] is False


class TestScaleRoundTrip:
    def test_fifty_fact_roundtrip(self, tmp_path):
        """结构化规模验证：50 事实存→召回往返（LongMemEval 类自建集为部署侧验收）"""
        conn = _fresh_conn(tmp_path)
        stored = 0
        for i in range(25):
            memory_semantic.store(conn, "tianshu", f"我偏好使用工具{i}号完成分析", audit_cb=_audit)
            memory_semantic.store(conn, "lingyun", f"我们服务于客户{i}号的品牌项目", audit_cb=_audit)
            stored += 2
        hits = 0
        for i in range(25):
            r1 = memory_semantic.recall(conn, "tianshu", f"工具{i}号偏好", top_k=3)
            r2 = memory_semantic.recall(conn, "lingyun", f"客户{i}号项目", top_k=3)
            hits += (1 if r1 else 0) + (1 if r2 else 0)
        assert stored == 50 and hits == 50, "50 事实存储→召回往返必须全部命中"


class TestHubEndpoints:
    def test_semantic_store_recall_forget_roundtrip(self, gov_client):
        store = gov_client.post("/memory/semantic/store", json={
            "agent": "tianshu", "text": "我偏好使用中文语言回答问题", "correlation_id": "sem-1"})
        assert store.status_code == 200
        results = store.get_json()["results"]
        assert results and results[0]["action"] == "stored"
        fid = results[0]["id"]

        recall = gov_client.get("/memory/semantic/recall?agent=tianshu&query=语言偏好").get_json()
        assert recall["memories"] and recall["memories"][0]["fact"]

        forget = gov_client.post("/memory/semantic/forget", json={
            "agent": "tianshu", "fact_id": fid, "correlation_id": "sem-2"})
        assert forget.get_json()["forgotten"] is True
        assert gov_client.get("/memory/semantic/recall?agent=tianshu&query=语言偏好").get_json()["memories"] == []

    def test_semantic_store_requires_text(self, gov_client):
        assert gov_client.post("/memory/semantic/store", json={"agent": "tianshu"}).status_code == 400

    def test_semantic_ops_in_audit_trail(self, gov_client):
        gov_client.post("/memory/semantic/store", json={
            "agent": "tianshu", "text": "我们来自 YanYuCloudCube 团队", "correlation_id": "sem-a1"})
        trail = gov_client.get("/audit/trail?limit=50").get_json()
        actions = [e.get("action") for e in trail]
        assert "memory_store" in actions, "语义记忆写入必须入审计链"
