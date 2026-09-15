import os
import json
from datetime import datetime, timedelta

class BusinessDecisionEngine:
    def __init__(self):
        self.risk_levels = ["低", "中", "高", "极高"]

    def generate_business_insight(self, data_sources: dict) -> dict:
        """生成经营洞察"""
        financial_data = data_sources.get("financial_data", {})
        market_data = data_sources.get("market_data", {})
        operational_data = data_sources.get("operational_data", {})

        revenue = financial_data.get("revenue", 0)
        costs = financial_data.get("costs", 0)
        profit_margin = ((revenue - costs) / revenue * 100) if revenue > 0 else 0

        market_growth = market_data.get("growth_rate", 0)
        competitor_count = market_data.get("competitor_count", 0)

        operational_efficiency = operational_data.get("efficiency_score", 70)

        overall_health_score = (
            min(profit_margin, 30) / 30 * 40 +
            min(max(market_growth, -10), 20) / 20 * 30 +
            operational_efficiency / 100 * 30
        )

        return {
            "task": "经营洞察",
            "generated_at": datetime.now().isoformat(),
            "financial_health": {
                "revenue": revenue,
                "costs": costs,
                "profit_margin": round(profit_margin, 2),
                "status": "良好" if profit_margin > 15 else ("警戒" if profit_margin > 5 else "危险")
            },
            "market_position": {
                "growth_rate": market_growth,
                "competitor_count": competitor_count,
                "market_share_trend": "上升" if market_growth > 10 else ("稳定" if market_growth > 0 else "下降")
            },
            "operational_status": {
                "efficiency_score": operational_efficiency,
                "status": "高效" if operational_efficiency > 80 else ("正常" if operational_efficiency > 60 else "需优化")
            },
            "overall_health_score": round(overall_health_score, 2),
            "key_insights": self._generate_key_insights(profit_margin, market_growth, operational_efficiency),
            "recommended_actions": self._generate_recommendations(overall_health_score)
        }

    def trend_prediction(self, historical_metrics: list) -> dict:
        """趋势预测"""
        if len(historical_metrics) < 3:
            return {"error": "历史数据不足，至少需要3个数据点"}

        recent_values = [m.get("value", 0) for m in historical_metrics[-6:]]

        if len(recent_values) >= 2:
            changes = [recent_values[i] - recent_values[i-1] for i in range(1, len(recent_values))]
            avg_change = sum(changes) / len(changes)
            trend_direction = "上升" if avg_change > 0 else ("下降" if avg_change < 0 else "稳定")
            volatility = (max(changes) - min(changes)) / abs(avg_change) if avg_change != 0 else 0
        else:
            avg_change = 0
            trend_direction = "数据不足"
            volatility = 0

        next_period_prediction = recent_values[-1] + avg_change if recent_values else 0

        confidence_level = "高" if volatility < 0.3 else ("中" if volatility < 0.7 else "低")

        risk_factors = []
        if volatility > 0.7:
            risk_factors.append("波动性较高，预测不确定性大")
        if avg_change < 0 and len([c for c in changes if c < 0]) > len(changes) * 0.7:
            risk_factors.append("持续下降趋势")

        return {
            "task": "趋势预测",
            "metric_name": historical_metrics[0].get("metric_name", "未知指标"),
            "current_value": recent_values[-1] if recent_values else 0,
            "trend_direction": trend_direction,
            "average_change": round(avg_change, 2),
            "next_period_prediction": round(next_period_prediction, 2),
            "volatility": round(volatility, 3),
            "confidence_level": confidence_level,
            "risk_factors": risk_factors if risk_factors else ["无明显风险因素"],
            "prediction_horizon": "下个周期"
        }

    def _generate_key_insights(self, profit_margin: float, market_growth: float, efficiency: float) -> list:
        insights = []

        if profit_margin > 20:
            insights.append({"type": "positive", "message": f"利润率优秀 ({profit_margin:.1f}%)，盈利能力强"})
        elif profit_margin < 5:
            insights.append({"type": "warning", "message": f"利润率偏低 ({profit_margin:.1f}%)，需关注成本控制"})

        if market_growth > 15:
            insights.append({"type": "positive", "message": f"市场增长强劲 ({market_growth:.1f}%)，扩张机会良好"})
        elif market_growth < 0:
            insights.append({"type": "critical", "message": f"市场萎缩 ({market_growth:.1f}%)，需调整战略"})

        if efficiency > 85:
            insights.append({"type": "positive", "message": f"运营效率优异 ({efficiency:.1f}分)，内部管理出色"})
        elif efficiency < 60:
            insights.append({"type": "warning", "message": f"运营效率待提升 ({efficiency:.1f}分)，需流程优化"})

        return insights if insights else [{"type": "info", "message": "各项指标平稳"}]

    def _generate_recommendations(self, health_score: float) -> list:
        if health_score >= 80:
            return [
                {"priority": "维持", "action": "保持当前策略，寻找增长机会"},
                {"priority": "探索", "action": "考虑市场扩张或新产品线"}
            ]
        elif health_score >= 60:
            return [
                {"priority": "重要", "action": "优化成本结构，提升利润率"},
                {"priority": "建议", "action": "加强市场分析，应对竞争压力"}
            ]
        else:
            return [
                {"priority": "紧急", "action": "立即进行全面的业务审查"},
                {"priority": "关键", "action": "制定转型或重组计划"}
            ]

def model_inference(input_data: dict) -> dict:
    engine = BusinessDecisionEngine()
    task_type = input_data.get("task")

    if task_type == "business_insight":
        return engine.generate_business_insight(input_data.get("data_sources", {}))
    elif task_type == "trend_prediction":
        return engine.trend_prediction(input_data.get("historical_metrics", []))
    else:
        return {"error": f"未知任务类型: {task_type}"}

if __name__ == "__main__":
    data_dir = os.environ.get("DATA_DIR", "/workspace/data")
    print(f"[Business Decision AI] 启动经营决策智能推理服务，数据目录: {data_dir}")

    for fname in os.listdir(data_dir):
        if fname.endswith('.json'):
            with open(os.path.join(data_dir, fname), 'r', encoding='utf-8') as f:
                input_data = json.load(f)
            result = model_inference(input_data)
            print(json.dumps(result, ensure_ascii=False, indent=2))
