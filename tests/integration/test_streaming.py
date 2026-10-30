"""E1-1 SSE 流式对话契约测试 — mock vLLM 上游分块，验证真实解析/治理兜底/零信任（Flask test_client）"""
import json

import agent_server
import pytest


class _FakeStreamResp:
    """模拟 vLLM OpenAI 兼容流式响应（含 usage 尾块与 [DONE] 哨兵）"""
    status_code = 200

    def raise_for_status(self):
        return None

    def iter_lines(self, decode_unicode=True):
        yield 'data: {"id":"c1","choices":[{"delta":{"role":"assistant","content":"你"}}]}'
        yield 'data: {"id":"c1","choices":[{"delta":{"content":"好"}}]}'
        yield 'data: {"id":"c1","choices":[{"delta":{},"finish_reason":"stop"}],"usage":{"prompt_tokens":10,"completion_tokens":2}}'
        yield "data: [DONE]"

    def close(self):
        return None


@pytest.fixture()
def agent_client(monkeypatch):
    monkeypatch.setattr(agent_server, "AGENT_NAME", "yuanqi_tianshu")
    monkeypatch.setattr(agent_server, "GOVERNANCE_ENDPOINT", "http://localhost:29998")  # 不可达 → 静默旁路
    return agent_server.app.test_client()


@pytest.fixture()
def mock_vllm_stream(monkeypatch):
    """仅拦截 /chat/completions；治理调用走真实 requests（不可达端口即静默旁路）"""
    real_post = agent_server.requests.post

    def fake_post(url, **kwargs):
        if url.endswith("/chat/completions"):
            assert kwargs.get("json", {}).get("stream") is True
            return _FakeStreamResp()
        return real_post(url, **kwargs)

    monkeypatch.setattr(agent_server.requests, "post", fake_post)


def _events(response):
    out = []
    for raw in response.get_data().decode("utf-8").split("\n\n"):
        line = raw.strip()
        if line.startswith("data: "):
            out.append(json.loads(line[len("data: "):]))
    return out


class TestChatStreamContract:
    def test_stream_requires_message(self, agent_client):
        assert agent_client.post("/chat/stream", json={}).status_code == 400

    def test_stream_relays_meta_delta_done(self, agent_client, mock_vllm_stream):
        r = agent_client.post("/chat/stream", json={"message": "你好"})
        assert r.status_code == 200
        assert r.content_type.startswith("text/event-stream")
        assert r.headers.get("X-Correlation-ID")
        events = _events(r)
        assert events[0]["type"] == "meta" and events[0]["correlation_id"] == r.headers["X-Correlation-ID"]
        deltas = [e for e in events if e["type"] == "delta"]
        assert "".join(e["content"] for e in deltas) == "你好"
        done = events[-1]
        assert done["type"] == "done"
        assert done["usage"]["prompt_tokens"] == 10 and done["usage"]["completion_tokens"] == 2
        assert "collaboration" in done

    def test_stream_upstream_down_emits_error_event(self, agent_client):
        r = agent_client.post("/chat/stream", json={"message": "你好"})  # vLLM 不可达
        assert r.status_code == 200
        events = _events(r)
        assert events[0]["type"] == "meta"
        assert events[-1]["type"] == "error"
        assert not any(e["type"] == "done" for e in events)

    def test_stream_auth_required_when_key_set(self, agent_client, monkeypatch, mock_vllm_stream):
        monkeypatch.setattr(agent_server, "AGENT_API_KEY", "k-test")
        assert agent_client.post("/chat/stream", json={"message": "hi"}).status_code == 401
        assert agent_client.post("/chat/stream", json={"message": "hi"},
                                 headers={"X-API-Key": "wrong"}).status_code == 401
        ok = agent_client.post("/chat/stream", json={"message": "hi"},
                               headers={"X-API-Key": "k-test"})
        assert ok.status_code == 200

    def test_stream_disconnect_still_reports_governance(self, agent_client, monkeypatch,
                                                        mock_vllm_stream):
        records = []
        monkeypatch.setattr(agent_server, "_governance_report",
                            lambda action, details, correlation_id="": records.append((action, details)))
        # 不经 test client（其上下文弹栈顺序跨 werkzeug 版本脆弱）：
        # 直接在 request context 中驱动生成器，meta 后 close 模拟客户端断开
        with agent_server.app.test_request_context("/chat/stream", method="POST",
                                                   json={"message": "你好"}):
            resp = agent_server.chat_stream()
            gen = iter(resp.response)
            next(gen)   # 仅消费 meta 事件
            gen.close()  # GeneratorExit → finally 兜底治理上报
        actions = [a for a, _ in records]
        assert "chat_request" in actions
        chat_response = [d for a, d in records if a == "chat_response"][0]
        assert chat_response["stream"] is True and chat_response["partial"] is True

    def test_capabilities_lists_stream_endpoint(self, agent_client):
        assert "/chat/stream" in agent_client.get("/capabilities").get_json()["endpoints"]
