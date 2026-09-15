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
    """P0-1 身份归一回归：生产全名（compose AGENT_NAME）上报必须命中治理
    （审计归属短名 / 预算生效 / 冻结生效）— hub.normalize_agent 归一入口"""

    FULL_TO_SHORT = {
        "yuanqi_tianshu": "tianshu", "yanqi_qianhang": "qianxing",
        "yushu_wanwu": "wanwu", "yujian_xianzhi": "xianzhi",
        "zhiyu_bole": "bole", "zhiyun_shouhu": "shouhu",
        "gewu_zongshi": "zongshi", "chuangxiang_lingyun": "lingyun",
    }

    def test_normalize_map_complete(self):
        from governance_hub import AGENT_ALIAS_MAP, normalize_agent
        assert AGENT_ALIAS_MAP == self.FULL_TO_SHORT
        for full, short in self.FULL_TO_SHORT.items():
            assert normalize_agent(full) == short
        assert normalize_agent("bole") == "bole"  # 短名幂等

    def test_full_name_budget_record_hits(self, gov_client):
        r = gov_client.post("/budget/record", json={
            "agent": "zhiyu_bole", "prompt_tokens": 100, "completion_tokens": 50})
        body = r.get_json()
        assert "error" not in body
        assert body["daily"]["used"] == 150  # 命中 bole 预算而非 Unknown agent

    def test_full_name_audit_uses_short_name(self, gov_client):
        gov_client.post("/audit/record", json={
            "agent": "yuanqi_tianshu", "action": "api_call", "details": {}})
        trail = gov_client.get("/audit/trail?agent=yuanqi_tianshu&limit=5").get_json()
        assert trail and all(e["agent"] == "tianshu" for e in trail)

    def test_full_name_kill_switch_then_frozen_check(self, gov_client):
        gov_client.post("/kill-switch", json={"agent": "zhiyu_bole", "reason": "drill"})
        states = {s["agent"]: s["state"] for s in gov_client.get("/agent-states").get_json()}
        assert states["bole"] == "frozen"
        gov_client.post("/unfreeze", json={"agent": "zhiyu_bole"})
        states = {s["agent"]: s["state"] for s in gov_client.get("/agent-states").get_json()}
        assert states["bole"] == "active"

    def test_full_name_collaboration_triggers(self, gov_client):
        body = gov_client.post("/collaboration/check", json={
            "primary_agent": "yuanqi_tianshu", "confidence": 0.5,
            "complexity": 0.2, "risk": "high"}).get_json()
        assert body["should_collaborate"] is True

    def test_all_short_names_registered(self):
        assert len(AGENTS) == 8
        assert set(self.FULL_TO_SHORT.values()) == set(AGENTS)


class TestZeroTrustAuthHub:
    """P0-2 零信任认证契约（hub 侧）：写操作须持有效 X-API-Key；读操作豁免；未配置 Key 为本地开放模式"""

    KEY = "test-hub-key"

    @pytest.fixture()
    def secure_client(self, gov_client, monkeypatch):
        import governance_hub
        monkeypatch.setattr(governance_hub, "GOVERNANCE_API_KEY", self.KEY)
        return gov_client

    def test_write_without_key_denied(self, secure_client):
        r = secure_client.post("/kill-switch", json={"agent": "tianshu", "reason": "drill"})
        assert r.status_code == 401
        body = r.get_json()
        assert body["error"] == "unauthorized"

    def test_write_with_wrong_key_denied(self, secure_client):
        r = secure_client.post("/kill-switch", json={"agent": "tianshu", "reason": "drill"},
                               headers={"X-API-Key": "wrong-key"})
        assert r.status_code == 401

    def test_write_with_valid_key_allowed(self, secure_client):
        r = secure_client.post("/audit/record", json={
            "agent": "tianshu", "action": "api_call", "details": {}},
            headers={"X-API-Key": self.KEY})
        assert r.status_code == 200

    def test_read_operations_exempt(self, secure_client):
        assert secure_client.get("/health").status_code == 200
        assert secure_client.get("/agent-states").status_code == 200

    def test_open_mode_when_key_unset(self, gov_client, monkeypatch):
        import governance_hub
        monkeypatch.setattr(governance_hub, "GOVERNANCE_API_KEY", "")
        r = gov_client.post("/kill-switch", json={"agent": "ALL", "reason": "drill"})
        assert r.status_code == 200


class TestZeroTrustAuthAgent:
    """P0-2 零信任认证契约（agent 侧）：/chat 写保护 + /health 读豁免 + 治理上报自动携带 Key"""

    KEY = "test-agent-key"

    @pytest.fixture()
    def secure_agent_client(self, agent_client, monkeypatch):
        monkeypatch.setattr(agent_server, "AGENT_API_KEY", self.KEY)
        return agent_client

    def test_chat_without_key_denied(self, secure_agent_client):
        r = secure_agent_client.post("/chat", json={"message": "你好"})
        assert r.status_code == 401
        assert r.get_json()["error"] == "unauthorized"

    def test_chat_with_wrong_key_denied(self, secure_agent_client):
        r = secure_agent_client.post("/chat", json={"message": "你好"}, headers={"X-API-Key": "bad"})
        assert r.status_code == 401

    def test_chat_with_valid_key_passes_auth(self, secure_agent_client):
        r = secure_agent_client.post("/chat", json={"message": "你好"},
                                     headers={"X-API-Key": self.KEY})
        assert r.status_code == 200  # 认证放行（vLLM 不可达 → 业务层 error 对象）

    def test_health_read_exempt(self, secure_agent_client):
        assert secure_agent_client.get("/health").status_code == 200

    def test_open_mode_when_key_unset(self, agent_client, monkeypatch):
        monkeypatch.setattr(agent_server, "AGENT_API_KEY", "")
        r = agent_client.post("/chat", json={"message": "你好"})
        assert r.status_code == 200

    def test_gov_headers_carries_key(self, monkeypatch):
        monkeypatch.setattr(agent_server, "GOVERNANCE_API_KEY", "gov-secret")
        assert agent_server._gov_headers()["X-API-Key"] == "gov-secret"
        monkeypatch.setattr(agent_server, "GOVERNANCE_API_KEY", "")
        assert "X-API-Key" not in agent_server._gov_headers()


class TestCorrelationIdContract:
    """P1-2 correlation_id 贯穿契约：/chat 自动生成 UUID 返回；调用方可传入自定义 ID；上报函数签名透传"""

    def test_chat_returns_uuid(self, agent_client):
        import uuid as uuid_mod
        r = agent_client.post("/chat", json={"message": "你好"})
        assert r.status_code == 200
        cid = r.get_json()["correlation_id"]
        uuid_mod.UUID(cid)  # 合法 UUID 格式（非法则抛 ValueError）

    def test_chat_honors_caller_supplied_id(self, agent_client):
        r = agent_client.post("/chat", json={"message": "你好", "correlation_id": "biz-123"})
        assert r.get_json()["correlation_id"] == "biz-123"

    def test_report_function_signature_passthrough(self, monkeypatch):
        captured = {}

        def fake_post(url, **kwargs):
            captured.update(kwargs["json"])

            class R:
                status_code = 200
                def json(self):
                    return []
            return R()

        monkeypatch.setattr(agent_server.requests, "post", fake_post)
        agent_server._governance_report("chat_request", {"x": 1}, correlation_id="corr-xyz")
        assert captured["correlation_id"] == "corr-xyz"
