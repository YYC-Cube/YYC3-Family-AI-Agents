#!/usr/bin/env python3
"""YYC³ FAmily-AI Telemetry (P2-3) — 轻量可观测门面

设计原则：
- OTel 为可选依赖：安装了 opentelemetry-api/sdk 则上报真 span；未安装自动降级为
  结构化 JSON 日志（INFO 级单行），保留 correlation_id 全链路追踪能力
- 零阻塞语义：任何遥测异常不得影响业务主流程
- 统一入口：trace_span() 上下文管理器 + record_event() 事件 + get_metrics() 内存指标快照
"""
import json
import logging
import os
import threading
import time
from contextlib import contextmanager
from datetime import datetime, timezone

logger = logging.getLogger("yyc3.telemetry")

TELEMETRY_LEVEL = os.environ.get("TELEMETRY_LEVEL", "info")  # debug|info|off
# P3-2 OTLP 导出：设置 YYC3_OTLP_ENDPOINT（如 http://otel-collector:4318）即启用 span 导出
OTLP_ENDPOINT = os.environ.get("YYC3_OTLP_ENDPOINT", "")

try:  # OTel 可选依赖：生产可 pip install opentelemetry-api opentelemetry-sdk 启用
    from opentelemetry import trace as _otel_trace  # type: ignore[import-not-found]
    if OTLP_ENDPOINT:
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter  # type: ignore[import-not-found]
        from opentelemetry.sdk.resources import Resource  # type: ignore[import-not-found]
        from opentelemetry.sdk.trace import TracerProvider  # type: ignore[import-not-found]
        from opentelemetry.sdk.trace.export import BatchSpanProcessor  # type: ignore[import-not-found]

        _provider = TracerProvider(resource=Resource.create({"service.name": "yyc3.family-ai"}))
        _provider.add_span_processor(BatchSpanProcessor(
            OTLPSpanExporter(endpoint=f"{OTLP_ENDPOINT.rstrip('/')}/v1/traces")))
        _otel_trace.set_tracer_provider(_provider)
        _OTEL_TRACER = _otel_trace.get_tracer("yyc3.family-ai")
        OTEL_AVAILABLE = True
        logger.info(f"OTel OTLP export enabled → {OTLP_ENDPOINT}")
    else:
        _OTEL_TRACER = _otel_trace.get_tracer("yyc3.family-ai")
        OTEL_AVAILABLE = True
except Exception:  # ImportError 或任何初始化失败 → 降级
    _OTEL_TRACER = None
    OTEL_AVAILABLE = False

# 内存指标（进程内快照，供 /dashboard 或调试端点读取）
_lock = threading.Lock()
_counters: dict = {}


def _bump(key: str, value: float = 1):
    with _lock:
        _counters[key] = _counters.get(key, 0) + value


def get_metrics() -> dict:
    with _lock:
        return {"counters": dict(_counters), "otel": OTEL_AVAILABLE}


def _log_event(level: str, name: str, correlation_id: str, attrs: dict, duration_ms=None):
    if TELEMETRY_LEVEL == "off":
        return
    payload = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "event": name,
        "correlation_id": correlation_id,
    }
    if duration_ms is not None:
        payload["duration_ms"] = round(duration_ms, 1)
    payload.update(attrs)
    logger.log(logging.getLevelName(level.upper()) if level.upper() in ("DEBUG", "INFO", "WARNING") else logging.INFO,
               json.dumps(payload, ensure_ascii=False))


@contextmanager
def trace_span(name: str, correlation_id: str = "", **attrs):
    """追踪一个阶段：OTel 在场则真 span，否则结构化日志（含时长）。永不抛异常。"""
    start = time.time()
    span = None
    if OTEL_AVAILABLE and _OTEL_TRACER is not None:
        try:
            span = _OTEL_TRACER.start_as_current_span(name)
            span.__enter__()
            if correlation_id:
                span.set_attribute("correlation_id", correlation_id)
            for k, v in attrs.items():
                span.set_attribute(k, v)
        except Exception:
            span = None
    try:
        yield
    except Exception:
        dur = (time.time() - start) * 1000
        _bump(f"span.{name}.error")
        if span is not None:
            try:
                span.record_exception(Exception("error"))
                span.__exit__(type("E", (Exception,), {}), Exception("error"), None)
            except Exception:
                pass
        _log_event("warning", name, correlation_id, {"status": "error"}, dur)
        raise
    else:
        dur = (time.time() - start) * 1000
        _bump(f"span.{name}.ok")
        if span is not None:
            try:
                span.__exit__(None, None, None)
            except Exception:
                pass
        _log_event("info", name, correlation_id, {"status": "ok"}, dur)


def record_event(name: str, correlation_id: str = "", level: str = "info", **attrs):
    """记录单点事件（无时长语义）。永不抛异常。"""
    try:
        _bump(f"event.{name}")
        _log_event(level, name, correlation_id, attrs)
    except Exception:
        pass
