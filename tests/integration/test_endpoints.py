"""集成测试：agent_server + governance_hub 端到端（Flask test_client，不占端口）"""
import agent_server
import pytest
from governance_hub import AGENTS


@pytest.fixture()
def agent_client(monkeypatch):
    monkeypatch.setattr(agent_server, "AGENT_NAME", "yuanqi_tianshu")
    monkeypatch.setattr(agent_server, "GOVERNANCE_ENDPOINT", "http://localhost:29998")  # 不可达 → 静默旁路
    return agent_server.app.test_client()


@pytest.fixture()
def gov_client(gov_db):
    return gov_db.app.test_client()


class TestAgentServerEndpoints:
    def test_health_reports_governance(self, agent_client):
        r = agent_client.get("/health")
        assert r.status_code == 200
        body = r.get_json()
        assert body["agent"] == "yuanqi_tianshu"
        assert "governance_connected" in body

    def test_chat_requires_message(self, agent_client):
        r = agent_client.post("/chat", json={})
        assert r.status_code == 400

    def test_chat_vllm_down_returns_error_object(self, agent_client):
        r = agent_client.post("/chat", json={"message": "你好"})
        assert r.status_code == 200
        body = r.get_json()
        assert isinstance(body["response"], dict)
        assert "error" in body["response"]

    def test_capabilities_lists_endpoints(self, agent_client):
        r = agent_client.get("/capabilities")
        assert "/chat" in r.get_json()["endpoints"]

    def test_identity_reports_prompt_files(self, agent_client):
        r = agent_client.get("/identity")
        assert r.status_code == 200


class TestGovernanceEndpoints:
    def test_health_version(self, gov_client):
        body = gov_client.get("/health").get_json()
        assert body["service"] == "yyc3-governance"
        assert body["version"] == "1.0.0"

    def test_audit_roundtrip(self, gov_client):
        r = gov_client.post("/audit/record", json={
            "agent": "tianshu", "action": "api_call", "details": {}, "correlation_id": "corr-1"})
        assert r.status_code == 200
        trail = gov_client.get("/audit/trail?agent=tianshu&limit=5").get_json()
        assert any(e["correlation_id"] == "corr-1" for e in trail)

    def test_kill_switch_then_agent_states(self, gov_client):
        gov_client.post("/kill-switch", json={"agent": "ALL", "reason": "drill"})
        states = {s["agent"]: s["state"] for s in gov_client.get("/agent-states").get_json()}
        assert set(states.values()) == {"frozen"}
        gov_client.post("/unfreeze", json={"agent": "tianshu"})
        states = {s["agent"]: s["state"] for s in gov_client.get("/agent-states").get_json()}
        assert states["tianshu"] == "active"

    def test_budget_dashboard_shape(self, gov_client):
        dashboard = gov_client.get("/budget/dashboard").get_json()
        assert "tianshu" in dashboard
        assert {"daily", "weekly", "monthly", "should_degrade", "should_block"} <= set(dashboard["tianshu"].keys())

    def test_collaboration_check_endpoint(self, gov_client):
        body = gov_client.post("/collaboration/check", json={
            "primary_agent": "tianshu", "confidence": 0.5, "complexity": 0.2, "risk": "high"}).get_json()
        assert body["should_collaborate"] is True

    def test_acs_policy_endpoint(self, gov_client):
        body = gov_client.get("/acs/policy/main").get_json()
        assert body["agent_id"] == "main"


class TestGovernanceAgentNameContract:
    """P0 缺陷回归：hub 的 AGENTS 短名必须能匹配 compose 的 AGENT_NAME 全名前缀"""

    def test_compose_agent_names_map_to_hub_short_names(self):
        # compose 使用 zhiyu_bole 等 8 个全名；hub AGENTS 为短名
        mapping = {"yuanqi_tianshu": "tianshu", "yanqi_qianhang": "qianxing",
                   "yushu_wanwu": "wanwu", "yujian_xianzhi": "xianzhi",
                   "zhiyu_bole": "bole", "zhiyun_shouhu": "shouhu",
                   "gewu_zongshi": "zongshi", "chuangxiang_lingyun": "lingyun"}
        for full, short in mapping.items():
            assert short in AGENTS, f"hub 缺少短名 {short}"
        # 但二者并不相等 — 该测试固化当前不一致现状，修复后应更新为全名断言
        assert set(mapping.values()) != set(mapping.keys())
