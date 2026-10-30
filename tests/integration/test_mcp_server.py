"""E2-2 治理中枢 MCP server 契约测试 — stateless JSON-RPC 2.0（initialize/ping/tools.list/tools.call）"""
import governance_hub
import pytest


@pytest.fixture()
def gov_client(gov_db):
    return gov_db.app.test_client()


def _rpc(client, method, req_id=1, params=None):
    payload = {"jsonrpc": "2.0", "id": req_id, "method": method}
    if params is not None:
        payload["params"] = params
    return client.post("/mcp", json=payload)


class TestMcpHandshake:
    def test_initialize_negotiates_protocol(self, gov_client):
        r = _rpc(gov_client, "initialize")
        assert r.status_code == 200
        body = r.get_json()
        assert body["jsonrpc"] == "2.0" and body["id"] == 1
        assert body["result"]["protocolVersion"] == "2026-07-28"
        assert body["result"]["serverInfo"]["name"] == "yyc3-governance-mcp"
        assert "tools" in body["result"]["capabilities"]

    def test_ping(self, gov_client):
        assert _rpc(gov_client, "ping").get_json()["result"] == {}


class TestMcpTools:
    def test_tools_list_exposes_three(self, gov_client):
        body = _rpc(gov_client, "tools/list").get_json()
        names = {t["name"] for t in body["result"]["tools"]}
        assert names == {"governance_budget_overview", "governance_audit_search",
                         "governance_agent_states"}
        for t in body["result"]["tools"]:
            assert t["inputSchema"]["type"] == "object"

    def test_tool_call_budget_overview(self, gov_client):
        r = _rpc(gov_client, "tools/call", params={
            "name": "governance_budget_overview", "arguments": {}})
        body = r.get_json()
        assert body["result"]["isError"] is False
        assert body["result"]["content"][0]["type"] == "text"
        assert "dashboard" in body["result"]["structuredContent"]

    def test_tool_call_agent_states(self, gov_client):
        r = _rpc(gov_client, "tools/call", params={
            "name": "governance_agent_states", "arguments": {}})
        states = r.get_json()["result"]["structuredContent"]["states"]
        assert isinstance(states, list)

    def test_tool_call_audit_search_with_agent_filter(self, gov_client):
        gov_client.post("/audit/record", json={
            "agent": "tianshu", "action": "mcp_probe", "details": {}, "correlation_id": "mcp-t1"})
        r = _rpc(gov_client, "tools/call", params={
            "name": "governance_audit_search", "arguments": {"agent": "tianshu", "limit": 5}})
        trail = r.get_json()["result"]["structuredContent"]["trail"]
        assert isinstance(trail, list) and len(trail) >= 1

    def test_tool_call_writes_audit_trail(self, gov_client):
        gov_client.post("/audit/record", json={
            "agent": "tianshu", "action": "seed", "details": {}, "correlation_id": "mcp-seed"})
        _rpc(gov_client, "tools/call", params={
            "name": "governance_agent_states", "arguments": {}}, req_id=42)
        trail = gov_client.get("/audit/trail?limit=50").get_json()
        mcp_rows = [e for e in trail if e.get("action") == "mcp_tool_call"]
        assert mcp_rows and any("mcp-42" in str(e.get("correlation_id")) for e in mcp_rows), \
            "tools/call 必须计入审计链（correlation_id 缺省由 JSON-RPC id 派生）"


class TestMcpErrors:
    def test_unknown_method_32601(self, gov_client):
        body = _rpc(gov_client, "resources/list").get_json()
        assert body["error"]["code"] == -32601

    def test_unknown_tool_32602(self, gov_client):
        body = _rpc(gov_client, "tools/call", params={"name": "nonexistent", "arguments": {}}).get_json()
        assert body["error"]["code"] == -32602 and "nonexistent" in body["error"]["message"]

    def test_invalid_request_32600(self, gov_client):
        r = gov_client.post("/mcp", json={"jsonrpc": "2.0", "id": 9})
        assert r.get_json()["error"]["code"] == -32600

    def test_notification_accepted_202(self, gov_client):
        r = gov_client.post("/mcp", json={"jsonrpc": "2.0", "method": "ping"})
        assert r.status_code == 202


class TestMcpZeroTrust:
    def test_write_protection_requires_key(self, gov_client, monkeypatch):
        KEY = "mcp-hub-key"
        monkeypatch.setattr(governance_hub, "GOVERNANCE_API_KEY", KEY)
        r = governance_hub.app.test_client().post(
            "/mcp", json={"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
        assert r.status_code == 401
        r2 = governance_hub.app.test_client().post(
            "/mcp", json={"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
            headers={"X-API-Key": KEY})
        assert r2.status_code == 200
