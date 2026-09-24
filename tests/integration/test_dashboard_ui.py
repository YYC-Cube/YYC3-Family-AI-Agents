"""P4-1/P4-2 Dashboard 契约：UI 挂载 + 数据面字段 + 周/月窗口 + Jaeger 跳转"""
import pytest


@pytest.fixture()
def gov_client(gov_db):
    return gov_db.app.test_client()


class TestDashboardUI:
    """hub / 挂载 dashboard.html，数据面 JSON API 不变"""

    def test_root_serves_html(self, gov_client):
        r = gov_client.get("/")
        assert r.status_code == 200
        assert "text/html" in r.content_type
        body = r.get_data(as_text=True)
        assert "治理中枢" in body
        assert "/dashboard" in body  # 前端数据源指向 JSON API

    def test_json_dashboard_unchanged(self, gov_client):
        r = gov_client.get("/dashboard")
        assert r.status_code == 200
        body = r.get_json()
        assert {"agents", "budgets", "behavior_events_total", "timestamp"} <= set(body.keys())

    def test_ui_reads_audit_trail_shape(self, gov_client):
        # 前端依赖 /audit/trail 返回数组（含 risk/correlation_id 字段）
        trail = gov_client.get("/audit/trail?limit=5").get_json()
        assert isinstance(trail, list)
        if trail:
            assert {"agent", "action", "risk", "correlation_id", "timestamp"} <= set(trail[0].keys())

    def test_ui_budget_fields_present(self, gov_client):
        # 前端进度条依赖 budgets.<agent>.daily.{used,limit}
        budgets = gov_client.get("/budget/dashboard").get_json()
        sample = next(iter(budgets.values()))
        assert "daily" in sample and "used" in sample["daily"] and "limit" in sample["daily"]


class TestWindowSwitchData:
    """前端周/月窗口切换依赖 budgets.<agent>.{daily,weekly,monthly}.pct"""

    def test_weekly_monthly_pct_present(self, gov_client):
        budgets = gov_client.get("/budget/dashboard").get_json()
        sample = budgets["bole"]
        for win in ("daily", "weekly", "monthly"):
            assert win in sample, f"缺窗口 {win}"
            assert {"used", "limit", "pct", "exceeded"} <= set(sample[win].keys())
            assert isinstance(sample[win]["pct"], (int, float))

    def test_ui_html_contains_window_switch_and_jaeger(self, gov_client):
        html = gov_client.get("/").get_data(as_text=True)
        assert "setWindow(" in html and "weekly" in html and "monthly" in html
        assert "openTrace(" in html and "16686" in html  # Jaeger 检索跳转
