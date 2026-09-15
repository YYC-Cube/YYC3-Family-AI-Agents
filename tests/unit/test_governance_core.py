"""单元测试：治理中枢核心引擎（审计/预算/协同/ACS/图谱）— 不起 HTTP"""
import pytest

from governance_hub import (
    AGENTS,
    ACSPolicyMapper,
    BehaviorAuditor,
    CollaborationEngine,
    ContextGraph,
    RiskLevel,
    TokenBudgetManager,
)


@pytest.fixture()
def auditor(gov_db):
    return BehaviorAuditor()


@pytest.fixture()
def budget(gov_db):
    return TokenBudgetManager()


@pytest.fixture()
def collab(gov_db):
    return CollaborationEngine()


class TestBehaviorAuditor:
    def test_record_low_risk_action(self, auditor):
        result = auditor.record("tianshu", "api_call", {"url": "/internal"})
        assert result["risk"] == "low"

    def test_dangerous_action_escalates(self, auditor):
        result = auditor.record("tianshu", "config_override", {})
        assert result["risk"] == "critical"

    def test_sensitive_keyword_in_details(self, auditor):
        # 契约：敏感数据细节须将风险提升至 HIGH（即使动作本身低危）
        result = auditor.record("tianshu", "file_read", {"path": "/etc/password"})
        assert result["risk"] == "high"

    def test_anomaly_critical_triggers_auto_freeze(self, auditor, gov_db):
        result = {"anomaly": {"level": "normal"}}
        for _ in range(55):  # 超过 critical=50 actions/min
            result = auditor.record("qianxing", "api_call")
        assert result["anomaly"]["level"] == "critical"
        trail = auditor.get_audit_trail("qianxing", limit=5)
        assert trail  # 审计已落库

    def test_kill_switch_freezes_all(self, auditor, gov_db):
        import sqlite3
        auditor.kill_switch("ALL", reason="test")
        conn = sqlite3.connect(gov_db.DB_PATH)
        states = dict(conn.execute("SELECT agent, state FROM agent_state").fetchall())
        conn.close()
        assert set(states.values()) == {"frozen"}
        assert auditor.unfreeze("tianshu")["state"] == "active"

    def test_audit_trail_ordering(self, auditor):
        auditor.record("wanwu", "file_read")
        auditor.record("wanwu", "api_call")
        trail = auditor.get_audit_trail("wanwu", limit=2)
        assert len(trail) == 2
        assert trail[0]["action"] == "api_call"  # DESC


class TestTokenBudget:
    def test_record_usage_increments(self, budget):
        status = budget.record_usage("tianshu", 1000, 500)
        assert status["daily"]["used"] == 1500
        assert status["daily"]["remaining"] == 500_000 - 1500

    def test_unknown_agent_rejected(self, budget):
        assert "error" in budget.record_usage("nonexistent", 1, 1)

    def test_should_degrade_at_80pct(self, budget):
        b = budget._budgets["shouhu"]
        b.used_today = int(200_000 * 0.81)
        status = budget._check_budget("shouhu")
        assert status["should_degrade"] is True
        assert status["should_block"] is False

    def test_should_block_at_100pct(self, budget):
        b = budget._budgets["shouhu"]
        b.used_today = 200_000
        status = budget._check_budget("shouhu")
        assert status["should_block"] is True

    def test_dashboard_covers_all_agents(self, budget):
        dashboard = budget.get_dashboard()
        assert set(dashboard.keys()) == set(AGENTS)


class TestCollaboration:
    def test_low_risk_no_trigger(self, collab):
        result = collab.should_collaborate("tianshu", confidence=0.95, complexity=0.1, risk="low")
        assert result["should_collaborate"] is False

    def test_high_risk_triggers_support(self, collab):
        result = collab.should_collaborate("tianshu", confidence=0.9, complexity=0.2, risk="high")
        assert result["should_collaborate"] is True
        supports = {t["support_agent"] for t in result["collaborators"]}
        assert "shouhu" in supports or "wanwu" in supports

    def test_fallback_chain_exists(self, collab):
        chain = collab.get_fallback("tianshu")
        assert "wanwu" in chain

    def test_sentinel_has_no_fallback(self, collab):
        # 安全官为最终权威，无降级链
        assert collab.get_fallback("shouhu") == []


class TestACS:
    def test_policy_generation(self):
        policy = ACSPolicyMapper().generate_policy("main")
        assert policy["display_name"] == "元启·天枢"
        assert policy["human_approval_required"] == ["strategic_decisions", "resource_reallocation"]
        assert policy["evidence_logging"]["log_all_actions"] is True

    def test_unknown_agent_falls_back_manual(self):
        policy = ACSPolicyMapper().generate_policy("ghost")
        assert policy["max_autonomy"] == "manual"


class TestContextGraph:
    def test_entity_relation_injection(self, gov_db):
        g = ContextGraph()
        g.add_entity("project", "yyc3-cube", {"owner": "yanyu"})
        g.add_relation("project", "yyc3-cube", "agent", "tianshu", "managed_by")
        result = g.inject_context("tianshu", "check yyc3-cube status")
        assert result["count"] >= 1
        assert any(e["id"] == "yyc3-cube" for e in result["injected_entities"])
        assert g.stats()["entities"] == 1

    def test_short_keywords_ignored(self, gov_db):
        g = ContextGraph()
        result = g.inject_context("tianshu", "a b ok")
        assert result["count"] == 0
