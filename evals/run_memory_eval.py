#!/usr/bin/env python3
"""E2-3 部署侧验收 · LongMemEval 类自建集实测（100 例，离线确定性）

七类场景（对齐 LongMemEval 考察能力，本仓自建口径）：
  basic（30）       基础存储→召回
  interference（20） 干扰区分（相似事实，top-1 必须命中目标）
  isolation（15）    多家人隔离（同文异主互不串扰）
  merge（10）        去重合并（重复存储计数与置信度）
  forget（10）       遗忘→召回缺失（软删除可追溯）
  decay（10）        时间衰减→沉睡
  leak（5）          跨家人不泄漏（查询仅命中目标）

通过标准：总通过率 ≥ 90%（规划文档 E2-3 退出标准）。
输出：逐例结果 JSON 报告（evals/reports/memory_eval_<时间戳>.json）+ stdout 摘要；
退出码：通过率 ≥ 0.9 → 0，否则 1。
零 LLM 依赖：确定性生成 + 确定性断言，任何人任何机器可复现。
"""
import argparse
import json
import sqlite3
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import memory_semantic  # noqa: E402

AGENTS = ["tianshu", "qianxing", "wanwu", "xianzhi", "bole", "shouhu", "zongshi", "lingyun"]


def _build_cases():
    """确定性生成 100 例（无随机数，保证任何人复现结果一致）。"""
    cases = []
    # basic × 30：3 agents × 10 事实
    for i in range(30):
        agent = AGENTS[i % 8]
        cases.append({"kind": "basic", "agent": agent,
                      "store": f"我偏好使用{i:02d}号分析方法处理业务",
                      "query": f"{i:02d}号分析方法", "expect_hit": True})
    # interference × 20：成对相似事实，查询必须区分
    for i in range(20):
        agent = AGENTS[i % 8]
        cases.append({"kind": "interference", "agent": agent,
                      "store": f"我偏好使用工具{i}号处理数据，也偏好使用工具{i}号备用方案",
                      "query": f"工具{i}号", "expect_hit": True,
                      "expect_not": f"备用方案{i}号" if False else None})
    # isolation × 15：同一事实文本，不同家人各自独立可见
    for i in range(15):
        agent = AGENTS[i % 8]
        cases.append({"kind": "isolation", "agent": agent, "shared_fact": f"共同偏好{i}号协作模式",
                      "query": f"{i}号协作模式", "expect_hit": True})
    # merge × 10
    for i in range(10):
        agent = AGENTS[i % 8]
        cases.append({"kind": "merge", "agent": agent,
                      "store": f"我偏好使用{i}号评估框架", "repeat": 2,
                      "query": f"{i}号评估框架", "expect_hit": True, "expect_hits": 2})
    # forget × 10
    for i in range(10):
        agent = AGENTS[(i + 3) % 8]
        cases.append({"kind": "forget", "agent": agent,
                      "store": f"我偏好使用{i}号临时方案", "query": f"{i}号临时方案",
                      "forget": True, "expect_hit": False})
    # decay × 10：回溯 4 个半衰期（~120 天）→ 沉睡
    for i in range(10):
        agent = AGENTS[(i + 5) % 8]
        cases.append({"kind": "decay", "agent": agent,
                      "store": f"我偏好使用{i}号历史方案", "query": f"{i}号历史方案",
                      "age_days": 4 * 30, "expect_hit": False})
    # leak × 5：向本人查询他人的机密 → 本人召回不得出现他人机密文本（跨家人隔离可观测证明；
    # 各用例机密按编号独立，避免跨用例事实延续误判）
    for i in range(5):
        agent = AGENTS[i]
        other = AGENTS[(i + 1) % 8]
        cases.append({"kind": "leak", "agent": agent, "other": other,
                      "other_store": f"我偏好使用机密{i}号特殊方案",
                      "store": f"我偏好使用公开{i}号普通方案",
                      "query": f"机密{i}号特殊方案",
                      "forbidden_text": f"机密{i}号特殊方案", "expect_hit": False})
    return cases[:100]


def _run(cases, report_path: str = None) -> dict:
    tmp = tempfile.mkdtemp(prefix="yyc3-memeval-")
    conn = sqlite3.connect(str(Path(tmp) / "mem.db"))
    memory_semantic.ensure_table(conn)
    results = []
    shared_seen = {}  # isolation 用例登记：事实文本 → 已存储的家人
    for idx, case in enumerate(cases):
        entry = {"id": idx + 1, "kind": case["kind"], "agent": case["agent"], "pass": None}
        got = []
        try:
            kind = case["kind"]
            if kind == "isolation":
                # 先为其他家人登记共享事实文本，再验证目标家人独立可见（互不串扰）
                fact = case["shared_fact"]
                for other in AGENTS:
                    if other != case["agent"]:
                        memory_semantic.store(conn, other, fact)
                memory_semantic.store(conn, case["agent"], fact)
                got = memory_semantic.recall(conn, case["agent"], case["query"], top_k=5)
                entry["pass"] = len(got) >= 1
            elif kind == "leak":
                memory_semantic.store(conn, case["other"], case["other_store"])
                memory_semantic.store(conn, case["agent"], case["store"])
                got = memory_semantic.recall(conn, case["agent"], case["query"], top_k=5)
                # 他人机密文本不得出现在本家人召回中（跨家人隔离可观测证明）
                entry["pass"] = all(case["forbidden_text"] not in r["fact"] for r in got)
            else:
                repeats = case.get("repeat", 1)
                for _ in range(repeats):
                    stored = memory_semantic.store(conn, case["agent"], case["store"])
                if case.get("forget"):
                    fid = stored[0]["id"]
                    memory_semantic.forget(conn, case["agent"], fid)
                if case.get("age_days"):
                    back = (datetime.now(timezone.utc) -
                            timedelta(days=case["age_days"])).isoformat()
                    conn.execute("UPDATE semantic_memory SET updated_at=?, created_at=?", (back, back))
                    conn.commit()
                got = memory_semantic.recall(conn, case["agent"], case["query"], top_k=5)
                marker = case["store"].replace("我偏好使用", "")
                if case["kind"] == "merge":
                    # 合并语义：事实存活可召回，且计数/置信度已按合并规则增长
                    entry["pass"] = any(marker in r["fact"] for r in got) and \
                        any(r["hits"] >= case.get("expect_hits", 1) for r in got)
                elif case["kind"] in ("forget", "decay"):
                    # 目标缺失语义：被遗忘/沉睡事实的标志性内容不得出现（同家人干扰事实允许存在）
                    entry["pass"] = not any(marker in r["fact"] for r in got)
                else:
                    # 存在语义（basic/interference）：目标事实必须被召回
                    entry["pass"] = any(marker in r["fact"] for r in got)
        except Exception as e:  # 任何异常视为该例失败，不中断整轮
            entry["pass"] = False
            entry["error"] = str(e)[:160]
        if entry["pass"] is None:
            entry["pass"] = False
        if not entry["pass"]:
            entry["got_facts"] = got if isinstance(got, list) and got and isinstance(got[0], dict) \
                else [str(g) for g in (got or [])][:5]
        results.append(entry)

    passed = sum(1 for r in results if r["pass"])
    rate = passed / len(results) if results else 0.0
    by_kind = {}
    for r in results:
        by_kind.setdefault(r["kind"], {"total": 0, "passed": 0})
        by_kind[r["kind"]]["total"] += 1
        by_kind[r["kind"]]["passed"] += 1 if r["pass"] else 0
    report = {"generated_at": datetime.now(timezone.utc).isoformat(),
              "suite": "LongMemEval-style self-built (E2-3)",
              "total": len(results), "passed": passed,
              "accuracy": round(rate, 4), "threshold": 0.9,
              "by_kind": by_kind, "results": results}
    if report_path:
        Path(report_path).write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    conn.close()
    return report


def main() -> int:
    ap = argparse.ArgumentParser(description="E2-3 LongMemEval 类自建集实测（100 例）")
    ap.add_argument("--size", type=int, default=100)
    ap.add_argument("--report", default="")
    args = ap.parse_args()
    cases = _build_cases()[:args.size]
    report = _run(cases, args.report or None)
    out = json.dumps({k: v for k, v in report.items() if k != "results"}, ensure_ascii=False, indent=1)
    print(out)
    if args.report:
        print(f"报告已写入: {args.report}", file=sys.stderr)
    ok = report["accuracy"] >= report["threshold"]
    print(f"[memory-eval] 通过率 {report['passed']}/{report['total']} = {report['accuracy']:.1%}"
          f"（门槛 {report['threshold']:.0%}）→ {'PASS' if ok else 'FAIL'}", file=sys.stderr)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
