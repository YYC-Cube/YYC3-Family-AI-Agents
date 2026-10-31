#!/usr/bin/env python3
"""E1-2 部署侧验收 · judge 一致率实测 — 真实 LLM 回答 × 规则断言 × LLM-judge 三方对照

对 golden set 逐例：
  1) 真实 LLM 回答（家人 SYSTEM.md 人设 + nemotron 端点）
  2) 规则断言（evaluate_rules：must_include_any/all · must_not_include · 长度界）
  3) LLM-judge 独立评分（是否满足验收要求；与规则断言对齐口径）
一致率口径：judge_pass 与 rule_pass 的判定一致率。报告：evals/reports/judge_consistency_first.json；
一致率 ≥85% 为 E1-2 退出标准。端点边界：http 白名单 + 主机显式允许列表（用户配置的推理节点）。
"""
import json
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "evals"))

from run_evals import evaluate_rules, load_golden  # noqa: E402

BASE = "http://100.126.132.112:10086/v1"
MODEL = "nemotron-3.5-super-vl"
ALLOWED_HOSTS = {"100.126.132.112"}  # 用户配置的推理节点（Tailscale 内网 ECS #33）
AGENTS_DIR = REPO / "agents"

AGENT_DIRS = {
    "tianshu": "yuanqi-tianshu", "qianxing": "yanqi-qianhang", "wanwu": "yushu-wanwu",
    "xianzhi": "yujian-xianzhi", "bole": "zhiyu-bole", "shouhu": "zhiyun-shouhu",
    "zongshi": "gewu-zongshi", "lingyun": "chuangxiang-lingyun",
}


def _validate_url(url: str) -> str:
    parts = urlsplit(url)
    if parts.scheme != "http" or not parts.hostname:
        raise ValueError(f"仅允许 http 且须含主机: {url}")
    if parts.username or parts.password:
        raise ValueError(f"禁止 URL 内嵌凭据: {url}")
    if parts.hostname not in ALLOWED_HOSTS:
        raise ValueError(f"目标主机不在允许列表: {parts.hostname}")
    return url


def chat(messages, max_tokens=512, temperature=0.7):
    url = _validate_url(f"{BASE}/chat/completions")
    payload = {"model": MODEL, "messages": messages, "max_tokens": max_tokens,
               "temperature": temperature,
               "chat_template_kwargs": {"enable_thinking": False}}
    data = None
    for attempt in (1, 2, 3):
        req = urllib.request.Request(
            url, data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            break
        except urllib.error.HTTPError as e:
            if e.code < 500 or attempt == 3:
                raise
            time.sleep(2 * attempt)
    content = data["choices"][0]["message"]["content"] or ""
    return content, data.get("usage", {})


def judge(question, answer, rules_desc):
    prompt = (
        "你是评估员。判断下面的回答是否通过该用例的验收要求。\n"
        f"验收要求：{rules_desc}\n用户问题：{question}\n回答：{answer[:1500]}\n"
        '只输出 JSON：{"pass": true/false, "score": 0-5, "reason": "一句话"}'
    )
    raw, _ = chat([{"role": "user", "content": prompt}], max_tokens=256, temperature=0.0)
    start, end = raw.find("{"), raw.rfind("}")
    if start < 0 or end <= start:
        return {"skipped": True, "raw": raw[:160]}
    try:
        parsed = json.loads(raw[start:end + 1])
        parsed["judge_pass"] = bool(parsed.get("pass"))
        return parsed
    except ValueError:
        return {"skipped": True, "raw": raw[:160]}


def main() -> int:
    golden = load_golden(REPO / "evals" / "golden" / "golden_cases.json")
    results = []
    for case in golden["cases"]:
        entry = {"id": case["id"], "agent": case["agent"], "category": case["category"],
                 "rules_pass": None, "violations": [], "answer_excerpt": "",
                 "prompt_tokens": 0, "completion_tokens": 0, "judge": None,
                 "agree": None, "error": None}
        try:
            agent = case["agent"]
            system_prompt = ""
            sp = AGENTS_DIR / AGENT_DIRS[agent] / "SYSTEM.md"
            if sp.exists():
                system_prompt = sp.read_text(encoding="utf-8").strip()
            answer, usage = chat([
                {"role": "system", "content": system_prompt or f"你是{agent}"},
                {"role": "user", "content": case["message"]},
            ])
            entry["answer_excerpt"] = answer[:200]
            entry["prompt_tokens"] = usage.get("prompt_tokens", 0)
            entry["completion_tokens"] = usage.get("completion_tokens", 0)
            ok, violations = evaluate_rules(answer, case.get("rules", {}))
            rules_desc = "; ".join(filter(None, [
                ("必须包含任一: " + ",".join(case["rules"].get("must_include_any", []))) if case["rules"].get("must_include_any") else "",
                ("必须包含全部: " + ",".join(case["rules"].get("must_include_all", []))) if case["rules"].get("must_include_all") else "",
                ("不得包含: " + ",".join(case["rules"].get("must_not_include", []))) if case["rules"].get("must_not_include") else "",
            ])) or "回答切题且专业"
            judge_result = judge(case["message"], answer, rules_desc or "回答切题")
            entry["judge"] = judge_result
            entry["rules_pass"] = ok
            entry["violations"] = violations
            entry["agree"] = (judge_result.get("judge_pass") is None) or \
                             (bool(judge_result.get("judge_pass")) == ok)
        except Exception as e:
            entry["error"] = f"{type(e).__name__}: {str(e)[:150]}"
        results.append(entry)
        flag = "ERR" if entry.get("error") else ("PASS" if entry["rules_pass"] else "FAIL")
        print(f"[{case['id']}] {flag} answer={entry['answer_excerpt'][:50]!r}", file=sys.stderr)

    rule_rate = sum(1 for r in results if r["rules_pass"]) / len(results)
    judged = [r for r in results if isinstance(r.get("judge"), dict) and not r["judge"].get("skipped")]
    agree_rate = (sum(1 for r in judged if r["agree"]) / len(judged)) if judged else 0.0
    report = {"generated_at": datetime.now(timezone.utc).isoformat(),
              "endpoint": BASE, "model": MODEL,
              "total": len(results), "rule_pass": sum(1 for r in results if r["rules_pass"]),
              "rule_rate": round(rule_rate, 4),
              "judged": len(judged), "agree_rate": round(agree_rate, 4),
              "threshold_agree": 0.85,
              "results": results}
    out = REPO / "evals" / "reports" / "judge_consistency_first.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "results"},
                     ensure_ascii=False, indent=1))
    ok = agree_rate >= 0.85 and rule_rate >= 0.9
    print(f"[judge-consistency] 规则通过率 {rule_rate:.0%} · 一致率 {agree_rate:.0%}（门槛 85%）"
          f" → {'PASS' if ok else 'FAIL'}", file=sys.stderr)
    return 0 if ok else 1


if __name__ == "__main__":
    main()
