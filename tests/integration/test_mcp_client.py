"""E2-1 MCP 客户端测试 — SSRF 边界单测 + 与治理中枢 /mcp 端点的真实 HTTP 回环联调"""
import ipaddress
import threading

import mcp_client
import pytest

import governance_hub


@pytest.fixture(scope="module")
def hub_live():
    """真实 HTTP 回环：werkzeug 起在 127.0.0.1:25710 固定端口（与家人 25600-25607 / hub 25700 错开）"""
    KEY = "loop-mcp-key"
    old = governance_hub.GOVERNANCE_API_KEY
    governance_hub.GOVERNANCE_API_KEY = KEY
    try:
        governance_hub.init_db()
    except Exception:
        pass
    from werkzeug.serving import make_server
    srv = make_server("127.0.0.1", 25710, governance_hub.app)
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    yield "http://127.0.0.1:25710/mcp", KEY
    srv.shutdown()
    governance_hub.GOVERNANCE_API_KEY = old


class TestUrlGuard:
    def test_rejects_non_http_scheme(self):
        with pytest.raises(ValueError):
            mcp_client._validate_url("ftp://example.com/mcp")

    def test_rejects_embedded_credentials(self):
        with pytest.raises(ValueError):
            mcp_client._validate_url("http://user:pass@example.com/mcp")

    def test_blocks_link_local_resolution(self):
        with pytest.raises(ValueError):
            mcp_client._validate_url("http://169.254.169.254/latest/meta-data/")

    def test_allows_loopback_and_private(self):
        assert mcp_client._validate_url("http://localhost:25700/mcp")
        assert mcp_client._validate_url("http://127.0.0.1:25700/mcp")
        assert mcp_client._validate_url("http://10.0.0.5:25700/mcp")
        assert mcp_client._validate_url("http://192.168.3.10/mcp")

    def test_loopback_ip_is_loopback(self):
        assert ipaddress.ip_address("127.0.0.1").is_loopback


class TestLiveLoopback:
    def test_initialize_handshake(self, hub_live):
        url, key = hub_live
        client = mcp_client.McpClient(url, api_key=key)
        result = client.initialize()
        assert result["protocolVersion"] == "2026-07-28"

    def test_auth_required_without_key(self, hub_live):
        url, _ = hub_live
        client = mcp_client.McpClient(url, api_key="")
        with pytest.raises(mcp_client.McpTransportError):
            client.initialize()

    def test_tools_list_and_call_roundtrip(self, hub_live):
        url, key = hub_live
        client = mcp_client.McpClient(url, api_key=key)
        tools = client.tools_list()["tools"]
        assert {t["name"] for t in tools} >= {"governance_budget_overview",
                                              "governance_agent_states"}
        result = client.tools_call("governance_agent_states", correlation_id="loop-cid-1")
        assert result["isError"] is False
        assert "states" in result["structuredContent"]

    def test_unknown_tool_raises_protocol_error(self, hub_live):
        url, key = hub_live
        client = mcp_client.McpClient(url, api_key=key)
        with pytest.raises(mcp_client.McpProtocolError) as ei:
            client.tools_call("nonexistent")
        assert ei.value.code == -32602

    def test_correlation_id_flows_to_audit(self, hub_live):
        import json as _json
        import urllib.request
        url, key = hub_live
        client = mcp_client.McpClient(url, api_key=key)
        client.tools_call("governance_agent_states", correlation_id="loop-cid-audit")
        base = url.rsplit("/mcp", 1)[0]
        audit_url = mcp_client._validate_url(f"{base}/audit/trail?limit=50")
        req = urllib.request.Request(audit_url, headers={"X-API-Key": key})
        with urllib.request.urlopen(req, timeout=10) as resp:
            trail = _json.loads(resp.read().decode("utf-8"))
        assert any("loop-cid-audit" in str(e.get("correlation_id"))
                   for e in trail if e.get("action") == "mcp_tool_call")
