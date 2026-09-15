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


class TestBudgetWindowReset:
    """P0-3 预算日重置契约：惰性跨窗清零（日/周/月），冷启动不误清，人工重置盖键一致"""

    def test_day_key_format(self):
        from governance_hub import day_key, month_key, week_key
        from datetime import datetime as dt, timezone as tz
        # 2026-01-01 为周四，ISO 周 2026-W01；周日 2026-01-04 仍在 W01，周一 01-05 进入 W02
        assert day_key(dt(2026, 1, 1, tzinfo=tz.utc)) == "2026-01-01"
        assert week_key(dt(2026, 1, 1, tzinfo=tz.utc)) == "2026-W01"
        assert week_key(dt(2026, 1, 4, tzinfo=tz.utc)) == "2026-W01"  # 周日不换周
        assert week_key(dt(2026, 1, 5, tzinfo=tz.utc)) == "2026-W02"  # 周一换周
        assert month_key(dt(2026, 1, 31, tzinfo=tz.utc)) == "2026-01"

    def test_lazy_daily_reset_on_record(self, budget, monkeypatch):
        budget.record_usage("tianshu", 100, 50)
        b = budget._budgets["tianshu"]
        assert b.used_today == 150
        # 模拟 yesterday 的窗口键（相同格式不同值）→ 下一笔记录应清零
        monkeypatch.setattr(b, "last_reset_daily", "2026-01-01")
        status = budget.record_usage("tianshu", 10, 5)
        assert b.used_today == 15
        assert status["daily"]["used"] == 15

    def test_lazy_weekly_and_monthly_reset(self, budget, monkeypatch):
        budget.record_usage("tianshu", 100, 50)
        b = budget._budgets["tianshu"]
        assert b.used_this_week == 150 and b.used_this_month == 150
        monkeypatch.setattr(b, "last_reset_weekly", "2025-W52")
        monkeypatch.setattr(b, "last_reset_monthly", "2025-12")
        budget.record_usage("tianshu", 10, 5)
        assert b.used_this_week == 15 and b.used_this_month == 15
        # 盖上当前窗口键（YYYY-Www / YYYY-MM 格式）
        import re
        assert re.fullmatch(r"\d{4}-W\d{2}", b.last_reset_weekly)
        assert re.fullmatch(r"\d{4}-\d{2}", b.last_reset_monthly)

    def test_cold_start_no_false_reset(self, budget):
        # last_reset_* 为空（冷启动）视为当前窗口，首笔记录后计数正常且不清理
        status = budget.record_usage("tianshu", 100, 50)
        assert status["daily"]["used"] == 150
        b = budget._budgets["tianshu"]
        assert b.last_reset_daily  # 已盖当前键

    def test_ensure_windows_same_day_noop(self, budget):
        budget.record_usage("tianshu", 100, 50)
        b = budget._budgets["tianshu"]
        budget._ensure_windows("tianshu")  # 同日重复检查不清零
        assert b.used_today == 150

    def test_manual_reset_daily_stamps_key(self, budget):
        budget.record_usage("tianshu", 100, 50)
        budget.reset_daily()
        b = budget._budgets["tianshu"]
        assert b.used_today == 0 and b.cost_today == 0.0
        # 人工重置后惰性检测不应再次清零（键已同步）
        from governance_hub import day_key
        from datetime import datetime as dt, timezone as tz
        assert b.last_reset_daily == day_key(dt.now(tz.utc))

    def test_check_budget_lazy_reset(self, budget, monkeypatch):
        budget.record_usage("tianshu", 100, 50)
        b = budget._budgets["tianshu"]
        monkeypatch.setattr(b, "last_reset_daily", "2026-01-01")
        status = budget._check_budget("tianshu")  # 只读入口也触发惰性重置
        assert status["daily"]["used"] == 0


class TestSQLiteHardening:
    """P1-3 SQLite 并发加固契约：connect_db 统一入口 WAL + busy_timeout，init_db 幂等"""

    def test_connect_db_enables_wal(self, gov_db):
        conn = gov_db.connect_db()
        mode = conn.execute("PRAGMA journal_mode").fetchone()[0]
        busy = conn.execute("PRAGMA busy_timeout").fetchone()[0]
        conn.close()
        assert mode == "wal"
        assert busy == 10000

    def test_concurrent_writes_no_lock_error(self, gov_db):
        # WAL 模式下并发写不应抛 database is locked
        import threading
        errors = []

        def write(i):
            try:
                conn = gov_db.connect_db()
                conn.execute(
                    "INSERT INTO behavior_events (agent, action, details, risk, correlation_id, timestamp) VALUES (?,?,?,?,?,?)",
                    ("tianshu", "concurrent_test", "{}", "low", f"c-{i}", "2026-01-01T00:00:00+00:00"))
                conn.commit()
                conn.close()
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=write, args=(i,)) for i in range(8)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert not errors, f"并发写失败: {errors}"

    def test_all_connections_via_factory(self, gov_db):
        # 生产代码统一走 connect_db 工厂：sqlite3.connect 仅允许出现在工厂定义内
        import inspect
        import governance_hub
        src = inspect.getsource(governance_hub)
        assert src.count("sqlite3.connect(DB_PATH") == 1  # 仅工厂内一处


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
