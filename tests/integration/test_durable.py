"""E3-3 持久化执行契约测试 — 步骤级 checkpoint / 断点恢复跳过推理 / 失败重试 / 预算零计费"""
import agent_server
import durable
import pytest


@pytest.fixture(autouse=True)
def _isolated_state(tmp_path, monkeypatch):
    """隔离：缓存清零 + durable DB 指向用例专属临时库"""
    agent_server._chat_cache.clear()
    agent_server._cache_stats.update({"hits": 0, "misses": 0})
    monkeypatch.setattr(durable, "DB_PATH", str(tmp_path / "durable.db"))
    yield


@pytest.fixture()
def agent_client(monkeypatch):
    monkeypatch.setattr(agent_server, "AGENT_NAME", "yuanqi_tianshu")
    monkeypatch.setattr(agent_server, "GOVERNANCE_ENDPOINT", "http://localhost:29998")
    return agent_server.app.test_client()


class _FakeNonStreamResp:
    def __init__(self, content):
        self.status_code = 200
        self._data = {"choices": [{"message": {"content": content}}],
                      "usage": {"prompt_tokens": 5, "completion_tokens": 3}}

    def raise_for_status(self):
        return None

    def json(self):
        return self._data


def _request_fingerprint(message, cid=None):
    """与 _execute_chat 内部同构的指纹计算（供测试预置 checkpoint）"""
    return durable.fingerprint({"message": message, "history": [],
                                "temperature": 0.7, "max_tokens": 4096,
                                "model": agent_server.VLLM_MODEL})


class TestFingerprint:
    def test_stable_for_same_input(self):
        a = durable.fingerprint({"message": "m", "history": [{"a": 1}, {"b": 2}]})
        b = durable.fingerprint({"message": "m", "history": [{"a": 1}, {"b": 2}]})
        assert a == b, "同输入指纹必须稳定"

    def test_history_order_participates(self):
        # 会话顺序影响生成语义，理应参与指纹
        assert durable.fingerprint({"message": "m", "history": [{"a": 1}, {"b": 2}]}) != \
            durable.fingerprint({"message": "m", "history": [{"b": 2}, {"a": 1}]})

    def test_differs_by_message(self):
        assert durable.fingerprint({"message": "a"}) != durable.fingerprint({"message": "b"})

    def test_ignores_correlation_id(self):
        assert "correlation_id" not in durable.fingerprint({"message": "m"})


class TestDurableResume:
    def test_llm_checkpoint_resumes_without_vllm(self, agent_client, monkeypatch):
        calls = []
        real_post = agent_server.requests.post

        def fake_post(url, **kwargs):
            if url.endswith("/chat/completions"):
                calls.append(url)
                return _FakeNonStreamResp("不应出现的实时回答")
            raise agent_server.requests.exceptions.ConnectionError(f"unreachable: {url}")

        monkeypatch.setattr(agent_server.requests, "post", fake_post)
        cid = "durable-resume-1"
        fp = _request_fingerprint("恢复测试")
        conn = durable.connect()
        durable.record_step(conn, cid, fp, "llm_inference", "done",
                            {"response": "断点恢复答案", "usage": {"prompt_tokens": 9}})
        conn.close()

        r = agent_client.post("/chat", json={"message": "恢复测试", "correlation_id": cid})
        assert r.status_code == 200
        body = r.get_json()
        assert body["response"] == "断点恢复答案"
        assert body["resumed_steps"] == ["llm_inference"]
        assert calls == [], "断点恢复不得重复调用 vLLM"

    def test_failure_then_retry_completes(self, agent_client, monkeypatch):
        state = {"fail_first": True}
        real_post = agent_server.requests.post

        def fake_post(url, **kwargs):
            if url.endswith("/chat/completions"):
                if state["fail_first"]:
                    state["fail_first"] = False
                    raise agent_server.requests.exceptions.ConnectionError("第一次失败")
                return _FakeNonStreamResp("重试成功")
            raise agent_server.requests.exceptions.ConnectionError(f"unreachable: {url}")

        monkeypatch.setattr(agent_server.requests, "post", fake_post)
        r1 = agent_client.post("/chat", json={"message": "重试场景", "correlation_id": "retry-1"})
        assert r1.status_code == 200
        assert isinstance(r1.get_json()["response"], dict), "首败返回错误对象"
        r2 = agent_client.post("/chat", json={"message": "重试场景", "correlation_id": "retry-1"})
        assert r2.get_json()["response"] == "重试成功"

    def test_different_message_no_resume(self, agent_client, monkeypatch):
        calls = []
        real_post = agent_server.requests.post

        def fake_post(url, **kwargs):
            if url.endswith("/chat/completions"):
                calls.append(url)
                return _FakeNonStreamResp("新回答")
            raise agent_server.requests.exceptions.ConnectionError(f"unreachable: {url}")

        monkeypatch.setattr(agent_server.requests, "post", fake_post)
        cid = "durable-diff-1"
        conn = durable.connect()
        durable.record_step(conn, cid, _request_fingerprint("旧问题"), "llm_inference", "done",
                            {"response": "旧答案", "usage": {}})
        conn.close()
        r = agent_client.post("/chat", json={"message": "全新问题", "correlation_id": cid})
        assert r.get_json()["response"] == "新回答"
        assert r.get_json()["resumed_steps"] == []
        assert len(calls) == 1

    def test_resume_zero_budget_charge(self, agent_client, monkeypatch):
        budget_rows = []
        real_post = agent_server.requests.post

        def fake_post(url, **kwargs):
            if url.endswith("/chat/completions"):
                return _FakeNonStreamResp("恢复答案")
            if url.endswith("/budget/record"):
                budget_rows.append(kwargs.get("json"))
                raise agent_server.requests.exceptions.ConnectionError("stop")
            raise agent_server.requests.exceptions.ConnectionError(f"unreachable: {url}")

        monkeypatch.setattr(agent_server.requests, "post", fake_post)
        cid = "durable-budget-1"
        conn = durable.connect()
        durable.record_step(conn, cid, _request_fingerprint("预算问题"), "llm_inference", "done",
                            {"response": "恢复答案", "usage": {"prompt_tokens": 9, "completion_tokens": 9}})
        conn.close()
        agent_client.post("/chat", json={"message": "预算问题", "correlation_id": cid})
        assert budget_rows and budget_rows[-1]["prompt_tokens"] == 0 \
            and budget_rows[-1]["completion_tokens"] == 0, "断点恢复预算零计费"
