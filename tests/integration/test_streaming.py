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


@pytest.fixture(autouse=True)
def _isolated_cache():
    """E1-3 缓存引入后：每用例清零模块级缓存，杜绝跨文件键污染"""
    agent_server._chat_cache.clear()
    agent_server._cache_stats.update({"hits": 0, "misses": 0})
    yield
    agent_server._chat_cache.clear()


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

    def test_stream_fallback_to_nonstream_when_no_sse_backup(self, agent_client, monkeypatch):
        """E1-3 降级矩阵流式兜底：建流全败（备援代理无 SSE）→ 回退非流式路径，
        SSE 合成 meta→delta(degraded 标记)→done，用量照常入预算"""
        monkeypatch.setattr(agent_server, "VLLM_ENDPOINT", "http://127.0.0.1:29991/v1")
        monkeypatch.setattr(agent_server, "VLLM_ENDPOINT_BACKUP", "http://127.0.0.1:29992/v1")
        real_post = agent_server.requests.post

        class _FakeNonStreamResp:
            status_code = 200

            def raise_for_status(self):
                return None

            def json(self):
                return {"choices": [{"message": {"content": "备援合成回答"}}],
                        "usage": {"prompt_tokens": 7, "completion_tokens": 3}}

        def fake_post(url, **kwargs):
            if url.endswith("/chat/completions"):
                if kwargs.get("json", {}).get("stream") is True:
                    raise agent_server.requests.exceptions.ConnectionError("proxy 无 SSE")
                return _FakeNonStreamResp()
            return real_post(url, **kwargs)

        monkeypatch.setattr(agent_server.requests, "post", fake_post)
        r = agent_client.post("/chat/stream", json={"message": "你好"})
        assert r.status_code == 200
        events = _events(r)
        assert [e["type"] for e in events] == ["meta", "delta", "done"]
        assert events[1]["content"] == "备援合成回答"
        assert events[1].get("degraded") == "nonstream_fallback"
        assert events[2]["usage"]["prompt_tokens"] == 7

    def test_stream_fallback_reports_degraded_audit(self, agent_client, monkeypatch):
        """流式兜底必留痕：model_degraded 审计 + model_failover 遥测（correlation_id 贯穿）"""
        monkeypatch.setattr(agent_server, "VLLM_ENDPOINT", "http://127.0.0.1:29991/v1")
        monkeypatch.setattr(agent_server, "VLLM_ENDPOINT_BACKUP", "http://127.0.0.1:29992/v1")
        records = []
        monkeypatch.setattr(agent_server, "_governance_report",
                            lambda action, details, correlation_id="": records.append((action, details)))
        real_post = agent_server.requests.post

        class _FakeNonStreamResp:
            status_code = 200

            def raise_for_status(self):
                return None

            def json(self):
                return {"choices": [{"message": {"content": "ok"}}],
                        "usage": {"prompt_tokens": 1, "completion_tokens": 1}}

        def fake_post(url, **kwargs):
            if url.endswith("/chat/completions"):
                if kwargs.get("json", {}).get("stream") is True:
                    raise agent_server.requests.exceptions.ConnectionError("no sse")
                return _FakeNonStreamResp()
            return real_post(url, **kwargs)

        monkeypatch.setattr(agent_server.requests, "post", fake_post)
        r = agent_client.post("/chat/stream", json={"message": "你好"})
        assert [e["type"] for e in _events(r)] == ["meta", "delta", "done"]
        degraded = [d for a, d in records if a == "model_degraded"]
        assert degraded and degraded[0]["stream_fallback"] is True
        assert degraded[0]["fallback"] == "nonstream_synth"

    def test_stream_checkpoints_and_resumes_llm_step(self, agent_client, monkeypatch, mock_vllm_stream):
        """E3-3 流式 checkpoint：首请求落 context_injection+llm_inference 两步；
        同 cid+指纹重入单 delta 回放（resumed 标记 + done.resumed=true + 预算零计费）。
        禁用语义缓存（生产语义：缓存为更廉价层先命中；此处单测 durable 层）"""
        monkeypatch.setattr(agent_server, "CHAT_CACHE_TTL", 0)
        import durable
        payload = {"message": "你好", "correlation_id": "cid-durable-stream-1"}
        r1 = agent_client.post("/chat/stream", json=payload)
        assert r1.status_code == 200
        ev1 = _events(r1)
        assert ev1[0]["type"] == "meta" and ev1[-1]["type"] == "done"
        assert "".join(e["content"] for e in ev1 if e["type"] == "delta") == "你好"
        assert ev1[-1]["resumed"] is False
        fp = durable.fingerprint({"message": "你好", "history": [],
                                  "temperature": 0.7, "max_tokens": 4096,
                                  "model": agent_server.VLLM_MODEL})
        conn = durable.connect()
        try:
            assert durable.get_step(conn, "cid-durable-stream-1", fp, "context_injection")
            assert durable.get_step(conn, "cid-durable-stream-1", fp, "llm_inference")
        finally:
            conn.close()
        r2 = agent_client.post("/chat/stream", json=payload)
        assert r2.status_code == 200
        ev2 = _events(r2)
        deltas = [e for e in ev2 if e["type"] == "delta"]
        assert len(deltas) == 1 and deltas[0].get("resumed") == "llm_inference"
        assert deltas[0]["content"] == "你好"
        assert ev2[-1]["type"] == "done" and ev2[-1]["resumed"] is True
        # done.usage 展示原始用量供参考；预算零计费验证：governance_token 收到 0/0
        token_calls = []
        monkeypatch.setattr(agent_server, "_governance_token",
                            lambda p, c, l, m, correlation_id="": token_calls.append((p, c)))
        _events(agent_client.post("/chat/stream", json=payload))  # 消费响应体驱动 finally
        assert token_calls and token_calls[-1] == (0, 0)

    def test_stream_fallback_output_also_checkpoints(self, agent_client, monkeypatch):
        """E3-3：非流式兜底产物同样落 checkpoint（跨路径可复用）"""
        monkeypatch.setattr(agent_server, "VLLM_ENDPOINT", "http://127.0.0.1:29991/v1")
        monkeypatch.setattr(agent_server, "VLLM_ENDPOINT_BACKUP", "http://127.0.0.1:29992/v1")
        import durable
        real_post = agent_server.requests.post

        class _FakeNonStreamResp:
            status_code = 200

            def raise_for_status(self):
                return None

            def json(self):
                return {"choices": [{"message": {"content": "兜底产物"}}],
                        "usage": {"prompt_tokens": 2, "completion_tokens": 1}}

        def fake_post(url, **kwargs):
            if url.endswith("/chat/completions"):
                if kwargs.get("json", {}).get("stream") is True:
                    raise agent_server.requests.exceptions.ConnectionError("no sse")
                return _FakeNonStreamResp()
            return real_post(url, **kwargs)

        monkeypatch.setattr(agent_server.requests, "post", fake_post)
        r = agent_client.post("/chat/stream", json={"message": "hi", "correlation_id": "cid-durable-fb"})
        assert [e["type"] for e in _events(r)] == ["meta", "delta", "done"]
        fp = durable.fingerprint({"message": "hi", "history": [],
                                  "temperature": 0.7, "max_tokens": 4096,
                                  "model": agent_server.VLLM_MODEL})
        conn = durable.connect()
        try:
            step = durable.get_step(conn, "cid-durable-fb", fp, "llm_inference")
        finally:
            conn.close()
        assert step and step["response"] == "兜底产物"
