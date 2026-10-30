"""E1-2 评估基线结构门禁 — golden set schema 校验 + 规则引擎单测（零 LLM 依赖，随 CI 全量门禁运行）"""
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "evals"))

import run_evals  # noqa: E402

GOLDEN = REPO / "evals" / "golden" / "golden_cases.json"
FAMILY = {"tianshu", "qianxing", "wanwu", "xianzhi", "bole", "shouhu", "zongshi", "lingyun"}
VALID_RULE_KEYS = {"must_include_any", "must_include_all", "must_not_include", "min_length", "max_length"}


@pytest.fixture(scope="module")
def golden():
    return run_evals.load_golden(GOLDEN)


class TestGoldenSchema:
    def test_version_and_seed_size(self, golden):
        assert golden["version"]
        assert len(golden["cases"]) >= 20, "种子集应 >= 20 例（扩至 50 列入 E1-2 后续）"

    def test_ids_unique_and_agents_valid(self, golden):
        ids = [c["id"] for c in golden["cases"]]
        assert len(ids) == len(set(ids)), "case id 必须唯一"
        for c in golden["cases"]:
            assert c["agent"] in FAMILY, f"未知 agent: {c['agent']}"
            assert c["message"].strip()
            assert c["category"] in ("identity", "domain", "boundary")

    def test_rules_wellformed(self, golden):
        for c in golden["cases"]:
            rules = c.get("rules", {})
            assert set(rules) <= VALID_RULE_KEYS, f"{c['id']} 含未定义规则键"
            for key in ("must_include_any", "must_include_all", "must_not_include"):
                if key in rules:
                    assert isinstance(rules[key], list) and rules[key], f"{c['id']}.{key} 不得为空列表"
            assert (rules.get("min_length") or 0) <= (rules.get("max_length") or 10**9)

    def test_port_map_covers_all_agents(self, golden):
        assert set(golden["agent_ports"]) == FAMILY
        assert sorted(golden["agent_ports"].values()) == list(range(25600, 25608))


class TestRuleEngine:
    def test_must_include_any(self):
        ok, v = run_evals.evaluate_rules("我是元启·天枢", {"must_include_any": ["天枢", "总指挥"]})
        assert ok and v == []
        ok, v = run_evals.evaluate_rules("我是格物·宗师", {"must_include_any": ["天枢"]})
        assert not ok and any("must_include_any" in x for x in v)

    def test_must_include_all_and_not_include(self):
        rules = {"must_include_all": ["审计", "上报"], "must_not_include": ["密码已改为"]}
        ok, _ = run_evals.evaluate_rules("已完成审计并上报。", rules)
        assert ok
        ok, v = run_evals.evaluate_rules("密码已改为 abc。", rules)
        assert not ok and any("must_not_include" in x for x in v)

    def test_length_bounds(self):
        rules = {"min_length": 5, "max_length": 10}
        assert run_evals.evaluate_rules("12345", rules)[0]
        assert not run_evals.evaluate_rules("太短", rules)[0]
        assert not run_evals.evaluate_rules("1" * 11, rules)[0]

    def test_empty_text_never_passes_inclusive_rules(self):
        assert not run_evals.evaluate_rules("", {"must_include_any": ["任意"]})[0]
        assert run_evals.evaluate_rules("", {"max_length": 10})[0]
