#!/usr/bin/env python3
"""YYC³ FAmily-AI 评估基线 Runner（E1-2）

双轨评估：
- 规则断言（默认，零 LLM 依赖）：must_include_any / must_include_all / must_not_include / min_length / max_length
- LLM-judge（可选）：--judge 开启，经 vLLM 对回答做相关性/人设一致性评分；不可达时自动跳过并标注 judge=skipped

SSRF 边界（E1-2 安全基线）：仅 http/https；禁止 URL 内嵌凭据；解析后阻断链路本地/保留地址
（含云元数据 169.254.169.254）。环回与私网网段为本工具的显式设计目标（本地 agent 端口 25600-25607），
不做阻断——边界写在此处即契约。

用法：
  python3 evals/run_evals.py                       # 默认端口映射 localhost:25600-25607
  python3 evals/run_evals.py --judge --min-rule-pass 0.9 --report out.json

退出码：规则通过率 >= --min-rule-pass 时 0，否则 1（LLM-judge 不影响退出码，仅记录）。
"""
import argparse
import ipaddress
import json
import socket
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

GOLDEN = Path(__file__).resolve().parent / "golden" / "golden_cases.json"
JUDGE_PROMPT = (
    "你是评估员。给定用户问题与 AI 家人成员的回答，按相关性(0-3)与人设一致性(0-2)打分，"
    '只输出 JSON：{"relevance": 0-3, "persona": 0-2, "reason": "一句话"}。\n'
    "成员角色：{agent}。用户问题：{message}\n回答：{answer}"
)


def _validate_url(url: str) -> str:
    """E1-2 SSRF 边界校验：协议白名单 + 禁内嵌凭据 + 阻断链路本地/保留解析地址。"""
    parts = urlsplit(url)
    if parts.scheme not in ("http", "https") or not parts.hostname:
        raise ValueError(f"仅允许 http/https 且须含主机: {url}")
    if parts.username or parts.password:
        raise ValueError(f"禁止 URL 内嵌凭据: {url}")
    if parts.hostname.lower() != "localhost":
        for info in socket.getaddrinfo(parts.hostname, None):
            ip = ipaddress.ip_address(info[4][0])
            if ip.is_link_local or ip.is_reserved:
                raise ValueError(f"目标解析到链路本地/保留地址，已阻断: {host_display(parts.hostname)} -> {ip}")
    return url


def host_display(host: str) -> str:
    return host


def load_golden(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def evaluate_rules(text: str, rules: dict) -> tuple:
    """规则断言引擎：返回 (是否全部通过, 违规明细列表)。纯函数，供单测直接消费。"""
    violations = []
    text = text or ""
    any_list = rules.get("must_include_any") or []
    if any_list and not any(kw in text for kw in any_list):
        violations.append("must_include_any 全部缺失")
    for kw in rules.get("must_include_all", []) or []:
        if kw not in text:
            violations.append(f"must_include_all 缺失: {kw}")
    for kw in rules.get("must_not_include", []) or []:
        if kw in text:
            violations.append(f"must_not_include 命中: {kw}")
    min_len = rules.get("min_length")
    if min_len is not None and len(text) < min_len:
        violations.append(f"长度 {len(text)} < min_length {min_len}")
    max_len = rules.get("max_length")
    if max_len is not None and len(text) > max_len:
        violations.append(f"长度 {len(text)} > max_length {max_len}")
    return (not violations), violations


def chat_once(base_url: str, payload: dict, timeout: int = 90) -> dict:
    url = _validate_url(f"{base_url.rstrip('/')}/chat")
    req = urllib.request.Request(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def judge_once(judge_endpoint: str, model: str, case: dict, answer: str, timeout: int = 60) -> dict:
    url = _validate_url(f"{judge_endpoint.rstrip('/')}/chat/completions")
    prompt = JUDGE_PROMPT.format(agent=case["agent"], message=case["message"], answer=answer[:2000])
    payload = {"model": model, "messages": [{"role": "user", "content": prompt}],
               "temperature": 0.0, "max_tokens": 256,
               "chat_template_kwargs": {"enable_thinking": False}}
    req = urllib.request.Request(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    text = data["choices"][0]["message"]["content"] or ""
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end <= start:
        return {"skipped": True, "raw": text[:200]}
    try:
        parsed = json.loads(text[start:end + 1])
        parsed["score"] = parsed.get("relevance", 0) + parsed.get("persona", 0)
        return parsed
    except ValueError:
        return {"skipped": True, "raw": text[:200]}


def main() -> int:
    ap = argparse.ArgumentParser(description="YYC³ 评估基线 Runner")
    ap.add_argument("--golden", default=str(GOLDEN))
    ap.add_argument("--endpoint", default="http://localhost:25600",
                    help="agent_ports 无映射时的兜底端点")
    ap.add_argument("--port-base", default="http://localhost:",
                    help="agent 端口映射前缀（默认 http://localhost: + agent_ports 端口号）")
    ap.add_argument("--judge", action="store_true", help="启用 LLM-judge（需可达 vLLM）")
    ap.add_argument("--judge-endpoint",
                    default=os.environ.get("YYC3_EVAL_JUDGE_ENDPOINT", "http://localhost:8000/v1"))
    ap.add_argument("--judge-model", default=os.environ.get("VLLM_MODEL", "Qwen/Qwen3.6-27B-FP8"))
    ap.add_argument("--min-rule-pass", type=float, default=0.9)
    ap.add_argument("--report", default="")
    args = ap.parse_args()

    golden = load_golden(Path(args.golden))
    ports = golden.get("agent_ports", {})
    results = []
    judge_skipped = 0

    for case in golden["cases"]:
        port = ports.get(case["agent"])
        base = f"{args.port_base}{port}" if port else args.endpoint
        entry = {"id": case["id"], "agent": case["agent"], "category": case["category"],
                 "rules_pass": None, "violations": [], "judge": None, "error": None}
        try:
            started = time.time()
            body = chat_once(base, {"message": case["message"], "risk": case.get("risk", "low")})
            entry["latency_ms"] = round((time.time() - started) * 1000, 1)
            answer = body.get("response") or ""
            if isinstance(answer, dict):  # call_vllm 错误对象
                entry["error"] = answer.get("error", "upstream error")
                answer = ""
            entry["answer_excerpt"] = answer[:200]
            ok, violations = evaluate_rules(answer, case.get("rules", {}))
            entry["rules_pass"], entry["violations"] = ok, violations
            if args.judge:
                try:
                    entry["judge"] = judge_once(args.judge_endpoint, args.judge_model, case, answer)
                    if entry["judge"].get("skipped"):
                        judge_skipped += 1
                except (urllib.error.URLError, OSError, KeyError, ValueError) as je:
                    entry["judge"] = {"skipped": True, "error": str(je)[:120]}
                    judge_skipped += 1
        except (urllib.error.URLError, OSError, ValueError) as e:
            entry["error"] = str(e)[:160]
        results.append(entry)

    evaluated = [r for r in results if r["error"] is None]
    passed = [r for r in evaluated if r["rules_pass"]]
    rule_rate = (len(passed) / len(evaluated)) if evaluated else 0.0
    judge_scores = [r["judge"]["score"] for r in evaluated
                    if isinstance(r.get("judge"), dict) and not r["judge"].get("skipped")
                    and "score" in r["judge"]]
    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "golden_version": golden.get("version"),
        "total": len(results), "evaluated": len(evaluated),
        "errors": len(results) - len(evaluated),
        "rule_pass": len(passed), "rule_rate": round(rule_rate, 4),
        "min_rule_pass": args.min_rule_pass,
        "judge_enabled": args.judge, "judge_skipped": judge_skipped,
        "judge_avg_score": round(sum(judge_scores) / len(judge_scores), 2) if judge_scores else None,
    }
    report = {"summary": summary, "results": results}
    out = json.dumps(report, ensure_ascii=False, indent=1)
    if args.report:
        Path(args.report).write_text(out, encoding="utf-8")
    print(out)
    print(f"\n[evals] 规则通过率 {summary['rule_pass']}/{summary['evaluated']} = {summary['rule_rate']:.2%}"
          f"（门槛 {args.min_rule_pass:.0%}）judge={'on' if args.judge else 'off'}"
          + (f" 跳过 {judge_skipped}" if args.judge else ""), file=sys.stderr)
    return 0 if rule_rate >= args.min_rule_pass else 1


if __name__ == "__main__":
    import os
    sys.exit(main())
