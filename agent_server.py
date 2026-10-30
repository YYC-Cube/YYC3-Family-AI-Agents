#!/usr/bin/env python3
"""
YYC³ FAmily-AI Agent Server v3.1 — 集成治理中枢

新增 (v3.1):
  - 每次推理自动上报行为审计
  - Token 使用量自动上报预算管理
  - 推理前检查 Agent 状态(是否被冻结)
  - 推理前注入上下文图谱
  - 推理后检查协同触发规则

用法: python agent_server.py --port <port> --role <role>
"""

import argparse
import hmac
import json
import logging
import os
import sys
import time
import uuid
from datetime import datetime, timezone

import requests
from flask import Flask, jsonify, request, Response, stream_with_context

import telemetry

app = Flask(__name__)

logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"),
                    format="%(asctime)s [%(name)s] %(levelname)s %(message)s")
logger = logging.getLogger(f"yyc3.agent.{os.environ.get('AGENT_NAME', 'unknown')}")

AGENT_NAME = os.environ.get("AGENT_NAME", "unknown")
AGENT_ROLE = os.environ.get("AGENT_ROLE", "unknown")
AGENT_LABEL = os.environ.get("AGENT_LABEL", "Unknown")
VLLM_ENDPOINT = os.environ.get("VLLM_ENDPOINT", "http://host.docker.internal:8000/v1")
VLLM_MODEL = os.environ.get("VLLM_MODEL", "Qwen/Qwen3.6-27B-FP8")
SYSTEM_PROMPT_PATH = os.environ.get("SYSTEM_PROMPT_PATH", "/workspace/SYSTEM.md")
GOVERNANCE_ENDPOINT = os.environ.get("GOVERNANCE_ENDPOINT", "http://localhost:25700")
GOVERNANCE_API_KEY = os.environ.get("GOVERNANCE_API_KEY", "")
AGENT_API_KEY = os.environ.get("AGENT_API_KEY", "")  # 空则 /chat 开放（本地开发）；生产必须配置
START_TIME = datetime.now(timezone.utc)

_system_prompt_cache = None


def load_system_prompt():
    global _system_prompt_cache
    if _system_prompt_cache is not None:
        return _system_prompt_cache
    try:
        with open(SYSTEM_PROMPT_PATH, "r", encoding="utf-8") as f:
            _system_prompt_cache = f.read().strip()
    except FileNotFoundError:
        _system_prompt_cache = f"你是{AGENT_LABEL}，YYC³ FAmily-AI 的成员。"
    return _system_prompt_cache


def _gov_headers():
    """治理上报携带共享 Key（hub 开放模式时空头亦可）"""
    h = {"Content-Type": "application/json"}
    if GOVERNANCE_API_KEY:
        h["X-API-Key"] = GOVERNANCE_API_KEY
    return h


WRITE_METHODS = {"POST", "PUT", "DELETE", "PATCH"}


def _constant_time_eq(a: str, b: str) -> bool:
    return hmac.compare_digest(a.encode("utf-8"), b.encode("utf-8"))


@app.before_request
def zero_trust_auth():
    """零信任写保护：写操作须持有效 X-API-Key；读操作与未配置 Key（本地开放模式）豁免"""
    if not AGENT_API_KEY:
        return None
    if request.method not in WRITE_METHODS:
        return None
    provided = request.headers.get("X-API-Key", "")
    if not provided or not _constant_time_eq(provided, AGENT_API_KEY):
        logger.warning(f"AUTH-DENIED: {request.method} {request.path} from {request.remote_addr}")
        return jsonify({"status": "error", "error": "unauthorized",
                        "detail": "Missing or invalid X-API-Key header"}), 401
    return None


def _governance_report(action, details, correlation_id=""):
    try:
        requests.post(f"{GOVERNANCE_ENDPOINT}/audit/record",
                      headers=_gov_headers(),
                      json={"agent": AGENT_NAME, "action": action,
                            "details": details, "correlation_id": correlation_id}, timeout=2)
    except Exception as e:
        logger.debug(f"[{correlation_id}] governance report '{action}' failed: {e}")

def _governance_token(prompt_tokens, completion_tokens, latency_ms, model, correlation_id=""):
    try:
        requests.post(f"{GOVERNANCE_ENDPOINT}/budget/record",
                      headers=_gov_headers(),
                      json={"agent": AGENT_NAME, "prompt_tokens": prompt_tokens,
                            "completion_tokens": completion_tokens,
                            "latency_ms": latency_ms, "model": model}, timeout=2)
    except Exception as e:
        logger.debug(f"[{correlation_id}] governance token report failed: {e}")

def _check_frozen():
    try:
        r = requests.get(f"{GOVERNANCE_ENDPOINT}/agent-states", timeout=2)
        for a in r.json():
            if a["agent"] == AGENT_NAME and a["state"] == "frozen":
                return True, a.get("frozen_reason", "Unknown")
    except Exception as e:
        logger.debug(f"governance frozen-check failed (treated as active): {e}")
    return False, ""

def _inject_context(user_message, correlation_id=""):
    try:
        r = requests.post(f"{GOVERNANCE_ENDPOINT}/context/inject",
                          headers=_gov_headers(),
                          json={"agent": AGENT_NAME, "task": user_message,
                                "correlation_id": correlation_id}, timeout=3)
        data = r.json()
        if data.get("count", 0) > 0:
            entities = data.get("injected_entities", [])
            ctx_str = "\n".join(f"  - {e['type']}/{e['id']}" for e in entities[:5])
            return f"\n\n## 动态上下文注入\n以下实体与当前任务相关:\n{ctx_str}"
    except Exception as e:
        logger.debug(f"[{correlation_id}] context injection failed (skipped): {e}")
    return ""

def _check_collaboration(user_message, confidence=1.0, complexity=0.5, risk="low", correlation_id=""):
    try:
        r = requests.post(f"{GOVERNANCE_ENDPOINT}/collaboration/check",
                          headers=_gov_headers(),
                          json={"primary_agent": AGENT_NAME, "confidence": confidence,
                                "complexity": complexity, "risk": risk,
                                "task_description": user_message,
                                "correlation_id": correlation_id}, timeout=3)
        return r.json()
    except Exception as e:
        logger.debug(f"[{correlation_id}] collaboration check failed (no collab): {e}")
        return {"should_collaborate": False}

def call_vllm(messages, temperature=0.7, max_tokens=4096):
    headers = {"Content-Type": "application/json"}
    payload = {"model": VLLM_MODEL, "messages": messages,
               "temperature": temperature, "max_tokens": max_tokens, "stream": False,
               "chat_template_kwargs": {"enable_thinking": False}}
    try:
        resp = requests.post(f"{VLLM_ENDPOINT}/chat/completions",
                             headers=headers, json=payload, timeout=120)
        resp.raise_for_status()
        data = resp.json()
        usage = data.get("usage", {})
        content = data["choices"][0]["message"]["content"]
        if content is None:
            content = data["choices"][0]["message"].get("reasoning", "") or "(模型推理超时,请增大max_tokens)"
        return content, usage
    except requests.exceptions.ConnectionError:
        return {"error": "vLLM endpoint unavailable", "endpoint": VLLM_ENDPOINT}, {}
    except Exception as e:
        return {"error": str(e)}, {}


def _iter_vllm_stream(messages, temperature=0.7, max_tokens=4096):
    """E1-1 vLLM OpenAI 兼容流式调用：yield SSE 原始 data 行；连接/HTTP 失败抛异常由调用方转 error 事件"""
    payload = {"model": VLLM_MODEL, "messages": messages,
               "temperature": temperature, "max_tokens": max_tokens,
               "stream": True, "stream_options": {"include_usage": True},
               "chat_template_kwargs": {"enable_thinking": False}}
    resp = requests.post(f"{VLLM_ENDPOINT}/chat/completions",
                         headers={"Content-Type": "application/json"},
                         json=payload, timeout=(5, 120), stream=True)
    resp.raise_for_status()
    try:
        for line in resp.iter_lines(decode_unicode=True):
            if line:
                yield line
    finally:
        resp.close()


def _sse(data: dict) -> str:
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"

@app.route("/health", methods=["GET"])
def health():
    uptime = (datetime.now(timezone.utc) - START_TIME).total_seconds()
    vllm_ok = False
    try:
        r = requests.get(f"{VLLM_ENDPOINT}/models", timeout=5)
        vllm_ok = r.status_code == 200
    except Exception:
        pass
    frozen, reason = _check_frozen()
    return jsonify({
        "status": "frozen" if frozen else ("healthy" if vllm_ok else "degraded"),
        "agent": AGENT_NAME, "label": AGENT_LABEL, "role": AGENT_ROLE,
        "uptime_seconds": round(uptime, 1), "vllm_reachable": vllm_ok,
        "model": VLLM_MODEL, "frozen": frozen, "frozen_reason": reason,
        "governance_connected": GOVERNANCE_ENDPOINT,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True)
    user_message = data.get("message", "")
    temperature = data.get("temperature", 0.7)
    max_tokens = data.get("max_tokens", 4096)
    history = data.get("history", [])
    risk = data.get("risk", "low")
    complexity = data.get("complexity", 0.5)

    if not user_message:
        return jsonify({"error": "message field is required"}), 400

    # P1-2 correlation_id 贯穿：一次对话的全部治理上报（审计/预算/上下文/协同）共享同一 UUID
    correlation_id = data.get("correlation_id") or str(uuid.uuid4())

    # P2-3 telemetry：对话主链路全阶段追踪（OTel 可选，降级为结构化日志）
    telemetry.record_event("chat_request", correlation_id, agent=AGENT_NAME,
                           message_len=len(user_message), risk=risk)

    with telemetry.trace_span("frozen_check", correlation_id, agent=AGENT_NAME):
        frozen, reason = _check_frozen()
    if frozen:
        telemetry.record_event("frozen_block", correlation_id, level="warning", agent=AGENT_NAME)
        _governance_report("frozen_block", {"reason": reason, "message": user_message[:100]},
                           correlation_id=correlation_id)
        return jsonify({"error": "Agent is frozen", "reason": reason, "agent": AGENT_NAME}), 403

    _governance_report("chat_request", {"message_len": len(user_message), "risk": risk},
                       correlation_id=correlation_id)

    with telemetry.trace_span("context_injection", correlation_id, agent=AGENT_NAME):
        system_prompt = load_system_prompt()
        context_injection = _inject_context(user_message, correlation_id=correlation_id)
        if context_injection:
            system_prompt += context_injection

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    with telemetry.trace_span("llm_inference", correlation_id, agent=AGENT_NAME, model=VLLM_MODEL):
        start = time.time()
        response, usage = call_vllm(messages, temperature=temperature, max_tokens=max_tokens)
        latency = round((time.time() - start) * 1000, 1)

    prompt_tokens = usage.get("prompt_tokens", 0)
    completion_tokens = usage.get("completion_tokens", 0)
    _governance_token(prompt_tokens, completion_tokens, latency, VLLM_MODEL,
                      correlation_id=correlation_id)

    _governance_report("chat_response", {"latency_ms": latency,
                                         "tokens": prompt_tokens + completion_tokens},
                       correlation_id=correlation_id)

    confidence = 0.85
    collab = _check_collaboration(user_message, confidence, complexity, risk,
                                  correlation_id=correlation_id)

    telemetry.record_event("chat_response", correlation_id, agent=AGENT_NAME,
                           latency_ms=latency,
                           tokens=prompt_tokens + completion_tokens)

    return jsonify({
        "agent": AGENT_NAME, "label": AGENT_LABEL, "role": AGENT_ROLE,
        "response": response,
        "correlation_id": correlation_id,
        "usage": usage, "latency_ms": latency,
        "collaboration": collab,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })

@app.route("/chat/stream", methods=["POST"])
def chat_stream():
    """E1-1 SSE 流式对话：预检与治理上报与 /chat 同构；逐 delta 转发 vLLM 流，
    断连/上游异常经 finally 兜底治理上报（partial 语义），预算与审计不因流式而旁路"""
    data = request.get_json(force=True)
    user_message = data.get("message", "")
    temperature = data.get("temperature", 0.7)
    max_tokens = data.get("max_tokens", 4096)
    history = data.get("history", [])
    risk = data.get("risk", "low")
    complexity = data.get("complexity", 0.5)

    if not user_message:
        return jsonify({"error": "message field is required"}), 400

    correlation_id = data.get("correlation_id") or str(uuid.uuid4())
    telemetry.record_event("chat_stream_request", correlation_id, agent=AGENT_NAME,
                           message_len=len(user_message), risk=risk)

    with telemetry.trace_span("frozen_check", correlation_id, agent=AGENT_NAME):
        frozen, reason = _check_frozen()
    if frozen:
        telemetry.record_event("frozen_block", correlation_id, level="warning", agent=AGENT_NAME)
        _governance_report("frozen_block", {"reason": reason, "message": user_message[:100]},
                           correlation_id=correlation_id)
        return jsonify({"error": "Agent is frozen", "reason": reason, "agent": AGENT_NAME}), 403

    _governance_report("chat_request", {"message_len": len(user_message), "risk": risk,
                                        "stream": True}, correlation_id=correlation_id)

    with telemetry.trace_span("context_injection", correlation_id, agent=AGENT_NAME):
        system_prompt = load_system_prompt()
        context_injection = _inject_context(user_message, correlation_id=correlation_id)
        if context_injection:
            system_prompt += context_injection

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    def generate():
        start = time.time()
        usage = {}
        pieces = []
        completed = False
        try:
            yield _sse({"type": "meta", "agent": AGENT_NAME, "label": AGENT_LABEL,
                        "role": AGENT_ROLE, "correlation_id": correlation_id,
                        "model": VLLM_MODEL})
            with telemetry.trace_span("llm_inference_stream", correlation_id,
                                      agent=AGENT_NAME, model=VLLM_MODEL):
                for line in _iter_vllm_stream(messages, temperature, max_tokens):
                    if not line.startswith("data:"):
                        continue
                    payload_text = line[len("data:"):].strip()
                    if payload_text == "[DONE]":
                        break
                    try:
                        chunk = json.loads(payload_text)
                    except ValueError:
                        continue
                    if chunk.get("usage"):
                        usage = chunk["usage"]
                    choices = chunk.get("choices") or []
                    delta = (choices[0].get("delta") or {}) if choices else {}
                    piece = delta.get("content")
                    if piece:
                        pieces.append(piece)
                        yield _sse({"type": "delta", "content": piece,
                                    "correlation_id": correlation_id})
            completed = True
        except Exception as e:
            yield _sse({"type": "error", "error": str(e)[:200],
                        "correlation_id": correlation_id})
        finally:
            latency = round((time.time() - start) * 1000, 1)
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)
            _governance_token(prompt_tokens, completion_tokens, latency, VLLM_MODEL,
                              correlation_id=correlation_id)
            _governance_report("chat_response", {"latency_ms": latency,
                                                 "tokens": prompt_tokens + completion_tokens,
                                                 "stream": True, "completed": completed,
                                                 "partial": not completed},
                               correlation_id=correlation_id)
            collab = _check_collaboration(user_message, confidence=0.85, complexity=complexity,
                                          risk=risk, correlation_id=correlation_id)
            telemetry.record_event("chat_stream_response", correlation_id, agent=AGENT_NAME,
                                   latency_ms=latency,
                                   tokens=prompt_tokens + completion_tokens,
                                   completed=completed)
            if completed:
                yield _sse({"type": "done", "correlation_id": correlation_id,
                            "usage": usage, "latency_ms": latency,
                            "collaboration": collab,
                            "timestamp": datetime.now(timezone.utc).isoformat()})

    resp = Response(stream_with_context(generate()), mimetype="text/event-stream")
    resp.headers["Cache-Control"] = "no-cache"
    resp.headers["X-Accel-Buffering"] = "no"
    resp.headers["X-Correlation-ID"] = correlation_id
    return resp

@app.route("/status", methods=["GET"])
def status():
    return jsonify({
        "agent": AGENT_NAME, "label": AGENT_LABEL, "role": AGENT_ROLE,
        "model": VLLM_MODEL, "vllm_endpoint": VLLM_ENDPOINT,
        "governance_endpoint": GOVERNANCE_ENDPOINT,
        "system_prompt_loaded": os.path.exists(SYSTEM_PROMPT_PATH),
        "uptime_seconds": round((datetime.now(timezone.utc) - START_TIME).total_seconds(), 1),
    })

@app.route("/identity", methods=["GET"])
def identity():
    identity_path = os.path.join(os.path.dirname(SYSTEM_PROMPT_PATH), "IDENTITY.md")
    soul_path = os.path.join(os.path.dirname(SYSTEM_PROMPT_PATH), "SOUL.md")
    result = {
        "agent": AGENT_NAME, "label": AGENT_LABEL, "role": AGENT_ROLE,
        "identity_loaded": os.path.exists(identity_path),
        "soul_loaded": os.path.exists(soul_path),
        "system_prompt_loaded": os.path.exists(SYSTEM_PROMPT_PATH),
    }
    if os.path.exists(identity_path):
        with open(identity_path, "r", encoding="utf-8") as f:
            result["identity_content"] = f.read().strip()
    return jsonify(result)

@app.route("/capabilities", methods=["GET"])
def capabilities():
    return jsonify({
        "agent": AGENT_NAME, "label": AGENT_LABEL, "role": AGENT_ROLE,
        "endpoints": ["/health", "/chat", "/chat/stream", "/status", "/capabilities", "/identity"],
        "model": VLLM_MODEL,
        "governance_integrated": True,
    })

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=f"YYC³ Agent Server — {AGENT_LABEL}")
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", 6000)))
    parser.add_argument("--role", type=str, default=AGENT_ROLE)
    args = parser.parse_args()
    logger.info(f"Starting {AGENT_LABEL} ({AGENT_NAME}) on port {args.port}")
    logger.info(f"vLLM: {VLLM_ENDPOINT} | Governance: {GOVERNANCE_ENDPOINT}")
    app.run(host="0.0.0.0", port=args.port, debug=False)
