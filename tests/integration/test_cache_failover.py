"""E1-3 缓存与降级矩阵契约测试 — mock vLLM 主备端点，验证缓存命中/关闭/降级审计（Flask test_client）"""
import json

import agent_server
import pytest


class _FakeNonStreamResp:
    def __init__(self, content, usage=None):
        self.status_code = 200
        self._data = {"choices": [{"message": {"content": content}}],
                      "usage": usage or {"prompt_tokens": 5, "completion_tokens": 3}}

    def raise_for_status(self):
        return None

    def json(self):
        return self._data


class _FakeStreamResp:
    status_code = 200

    def raise_for_status(self):
        return None

    def iter_lines(self, decode_unicode=True):
        yield 'data: {"id":"c1","choices":[{"delta":{"content":"流式答案"}}]}'
        yield 'data: {"id":"c1","choices":[{"delta":{},"finish_reason":"stop"}],"usage":{"prompt_tokens":7,"completion_tokens":4}}'
        yield "data: [DONE]"

    def close(self):
        return None


@pytest.fixture(autouse=True)
def _isolated_cache():
    """模块级缓存在用例间清零，杜绝跨文件键污染（流式/非流式共享键空间）"""
    agent_server._chat_cache.clear()
    agent_server._cache_stats.update({"hits": 0, "misses": 0})
    yield
    agent_server._chat_cache.clear()


@pytest.fixture()
def agent_client(monkeypatch):
    monkeypatch.setattr(agent_server, "AGENT_NAME", "yuanqi_tianshu")
    monkeypatch.setattr(agent_server, "GOVERNANCE_ENDPOINT", "http://localhost:29998")
    return agent_server.app.test_client()


@pytest.fixture()
def gov_records(monkeypatch):
    records = []
    monkeypatch.setattr(agent_server, "_governance_report",
                        lambda action, details, correlation_id="": records.append((action, details)))
    return records


def _install_endpoints(monkeypatch, calls, primary_mode, backup_content="备援答案"):
    """primary_mode: 'down'（连接拒绝）| 'ok'；backup 始终可用；记录全部 /chat/completions 调用"""
    real_post = agent_server.requests.post

    def fake_post(url, **kwargs):
        if url.endswith("/chat/completions"):
            calls.append({"url": url, "stream": kwargs.get("json", {}).get("stream", False)})
            if url.startswith("http://primary") and primary_mode == "down":
                raise agent_server.requests.exceptions.ConnectionError("primary down")
            if kwargs.get("json", {}).get("stream"):
                return _FakeStreamResp()
            return _FakeNonStreamResp(backup_content)
        raise agent_server.requests.exceptions.ConnectionError(f"unreachable: {url}")

    monkeypatch.setattr(agent_server.requests, "post", fake_post)


class TestSemanticCache:
    def test_cache_hit_second_call_skips_vllm(self, agent_client, monkeypatch):
        calls = []
        _install_endpoints(monkeypatch, calls, primary_mode="ok", backup_content="答案A")
        monkeypatch.setattr(agent_server, "VLLM_ENDPOINT", "http://primary:8000/v1")
        r1 = agent_client.post("/chat", json={"message": "同一个问题"})
        r2 = agent_client.post("/chat", json={"message": "同一个问题"})
        assert r1.status_code == 200 and r2.status_code == 200
        assert r1.get_json()["cached"] is False and r2.get_json()["cached"] is True
        assert r2.get_json()["response"] == r1.get_json()["response"]
        assert len(calls) == 1, "第二次命中缓存，不得再调 vLLM"
        status = agent_client.get("/status").get_json()["cache"]
        assert status["enabled"] is True and status["hits"] >= 1

    def test_cache_disabled_env(self, agent_client, monkeypatch):
        calls = []
        _install_endpoints(monkeypatch, calls, primary_mode="ok", backup_content="答案A")
        monkeypatch.setattr(agent_server, "VLLM_ENDPOINT", "http://primary:8000/v1")
        monkeypatch.setattr(agent_server, "CHAT_CACHE_TTL", 0)
        agent_client.post("/chat", json={"message": "问题"})
        agent_client.post("/chat", json={"message": "问题"})
        assert len(calls) == 2, "TTL=0 时缓存关闭，两次都应触达 vLLM"

    def test_expired_entry_not_served(self, agent_client, monkeypatch):
        _install_endpoints(monkeypatch, [], primary_mode="ok", backup_content="答案A")
        monkeypatch.setattr(agent_server, "VLLM_ENDPOINT", "http://primary:8000/v1")
        agent_server._cache_put("stale-key", "旧答案", {"prompt_tokens": 1, "completion_tokens": 1})
        agent_server._chat_cache["stale-key"]["ts"] -= agent_server.CHAT_CACHE_TTL + 1
        assert agent_server._cache_get("stale-key") is None


class TestFailoverMatrix:
    def test_nonstream_failover_to_backup_with_audit(self, agent_client, monkeypatch, gov_records):
        calls = []
        _install_endpoints(monkeypatch, calls, primary_mode="down")
        monkeypatch.setattr(agent_server, "VLLM_ENDPOINT", "http://primary:8000/v1")
        monkeypatch.setattr(agent_server, "VLLM_ENDPOINT_BACKUP", "http://backup:8000/v1")
        r = agent_client.post("/chat", json={"message": "你好", "correlation_id": "fo-1"})
        assert r.status_code == 200
        assert r.get_json()["response"] == "备援答案"
        assert [c["url"].split("//")[1].split(":")[0] for c in calls] == ["primary", "backup"]
        degraded = [d for a, d in gov_records if a == "model_degraded"]
        assert degraded and degraded[0]["backup"] == "http://backup:8000/v1"

    def test_stream_failover_to_backup(self, agent_client, monkeypatch):
        calls = []
        _install_endpoints(monkeypatch, calls, primary_mode="down")
        monkeypatch.setattr(agent_server, "VLLM_ENDPOINT", "http://primary:8000/v1")
        monkeypatch.setattr(agent_server, "VLLM_ENDPOINT_BACKUP", "http://backup:8000/v1")
        r = agent_client.post("/chat/stream", json={"message": "你好"})
        assert r.status_code == 200
        body = r.get_data().decode("utf-8")
        assert "流式答案" in body and '"type": "error"' not in body
        assert sum(1 for c in calls if c["url"].startswith("http://backup")) == 1

    def test_status_reports_backup_and_cache(self, agent_client):
        body = agent_client.get("/status").get_json()
        assert body["vllm_backup_configured"] is False
        assert body["cache"]["enabled"] is True and "hits" in body["cache"]
