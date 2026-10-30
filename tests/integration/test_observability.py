"""P2-2 /prompts/* 模板下发 + P2-3 telemetry 契约测试"""
import agent_server
import pytest
import telemetry


@pytest.fixture()
def gov_client(gov_db):
    return gov_db.app.test_client()


@pytest.fixture()
def agent_client(monkeypatch):
    monkeypatch.setattr(agent_server, "AGENT_NAME", "yuanqi_tianshu")
    monkeypatch.setattr(agent_server, "GOVERNANCE_ENDPOINT", "http://localhost:29998")
    return agent_server.app.test_client()


class TestPromptsEndpoints:
    """P2-2 模板版本化下发契约（hub 侧）"""

    def test_overview_lists_templates(self, gov_client):
        r = gov_client.get("/prompts/bole")
        assert r.status_code == 200
        body = r.get_json()
        assert body["agent"] == "bole"
        assert {"IDENTITY.md", "SOUL.md", "SYSTEM.md"} <= set(body["templates"].keys())
        for meta in body["templates"].values():
            assert len(meta["sha256"]) == 64 and meta["size"] > 0

    def test_get_template_text(self, gov_client):
        r = gov_client.get("/prompts/bole/SYSTEM.md")
        assert r.status_code == 200
        assert "text/markdown" in r.content_type
        assert "千里·伯乐" in r.get_data(as_text=True)

    def test_get_template_json_with_hash(self, gov_client):
        r = gov_client.get("/prompts/tianshu/SOUL.md?format=json")
        body = r.get_json()
        assert body["status"] == "ok" and body["agent"] == "tianshu"
        assert len(body["sha256"]) == 64 and "元启·天枢" in body["content"]

    def test_full_name_alias_supported(self, gov_client):
        # P0-1 归一联动：/prompts/zhiyu_bole/* 应与 /prompts/bole/* 同源
        r = gov_client.get("/prompts/zhiyu_bole/SYSTEM.md?format=json")
        assert r.get_json()["agent"] == "bole"

    def test_unknown_template_404(self, gov_client):
        assert gov_client.get("/prompts/bole/unknown.md").status_code == 404

    def test_unknown_agent_404(self, gov_client):
        assert gov_client.get("/prompts/nonexistent").status_code == 404


class TestTelemetryModule:
    """P2-3 telemetry 门面契约（降级模式，OTel 未安装）"""

    def test_trace_span_ok_records_counter(self):
        with telemetry.trace_span("unit_probe", correlation_id="c-1", agent="x"):
            pass
        metrics = telemetry.get_metrics()
        assert metrics["counters"]["span.unit_probe.ok"] >= 1

    def test_trace_span_error_reraises_and_counts(self):
        with pytest.raises(ValueError):
            with telemetry.trace_span("unit_fail", correlation_id="c-2"):
                raise ValueError("boom")
        assert telemetry.get_metrics()["counters"]["span.unit_fail.error"] >= 1

    def test_record_event_never_raises(self):
        telemetry.record_event("probe_event", correlation_id="c-3", k="v")
        assert telemetry.get_metrics()["counters"]["event.probe_event"] >= 1

    def test_metrics_reports_otel_availability(self):
        assert "otel" in telemetry.get_metrics()


class TestChatTelemetryWiring:
    """agent /chat 链路 telemetry 接线（不真调 vLLM）"""

    def test_chat_emits_events(self, agent_client, monkeypatch):
        before = telemetry.get_metrics()["counters"].copy()
        r = agent_client.post("/chat", json={"message": "你好", "correlation_id": "tel-1"})
        assert r.status_code == 200
        after = telemetry.get_metrics()["counters"]
        assert after.get("event.chat_request", 0) >= before.get("event.chat_request", 0) + 1
        assert after.get("event.chat_response", 0) >= before.get("event.chat_response", 0) + 1
        assert after.get("span.llm_inference.ok", 0) >= before.get("span.llm_inference.ok", 0) + 1

    def test_hub_metrics_endpoint(self, gov_client):
        r = gov_client.get("/metrics")
        assert r.status_code == 200
        body = r.get_json()
        assert body["status"] == "ok" and "counters" in body and "otel" in body


class TestGenAISemanticConventions:
    """E1-4 OTel GenAI 语义约定（gen_ai.* 属性组，降级模式断言日志负载）"""

    def test_genai_attrs_shape(self):
        attrs = telemetry.genai_attrs(model="Qwen/Qwen3.6-27B-FP8", agent="tianshu",
                                      **{"gen_ai.usage.prompt_tokens": 10})
        assert attrs["gen_ai.system"] == "vllm"
        assert attrs["gen_ai.operation.name"] == "chat"
        assert attrs["gen_ai.request.model"] == "Qwen/Qwen3.6-27B-FP8"
        assert attrs["gen_ai.agent.name"] == "tianshu"
        assert attrs["gen_ai.usage.prompt_tokens"] == 10

    def test_trace_span_accepts_attrs_dict(self, caplog):
        import json as _json
        with caplog.at_level("INFO", logger="yyc3.telemetry"):
            with telemetry.trace_span("genai_probe", correlation_id="c-g1",
                                      attrs=telemetry.genai_attrs(model="m1", agent="tianshu")):
                pass
        payload = _json.loads(caplog.records[-1].message)
        assert payload["gen_ai.request.model"] == "m1"
        assert payload["gen_ai.agent.name"] == "tianshu"

    def test_chat_response_event_carries_genai_usage(self, agent_client, caplog):
        import json as _json
        with caplog.at_level("INFO", logger="yyc3.telemetry"):
            r = agent_client.post("/chat", json={"message": "你好", "correlation_id": "genai-1"})
        assert r.status_code == 200
        genai_rows = [_json.loads(rec.message) for rec in caplog.records
                      if "gen_ai.usage.prompt_tokens" in rec.getMessage()]
        assert genai_rows, "chat_response 降级日志应携带 gen_ai.usage.*"
        assert genai_rows[-1]["gen_ai.agent.name"] == "yuanqi_tianshu"
        assert genai_rows[-1]["gen_ai.operation.name"] == "chat"
