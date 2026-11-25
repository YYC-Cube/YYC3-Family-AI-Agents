import os
import json
from datetime import datetime, timedelta

class SalesInferenceEngine:
    def __init__(self):
        self.seasonal_factors = {
            "Q1": 0.85,
            "Q2": 1.05,
            "Q3": 1.15,
            "Q4": 1.35
        }

    def sales_trend_analysis(self, historical_data: list) -> dict:
        """销售趋势分析"""
        if not historical_data:
            return {"error": "无历史数据"}

        monthly_sales = [d.get("sales_amount", 0) for d in historical_data]

        if len(monthly_sales) >= 3:
            recent_avg = sum(monthly_sales[-3:]) / 3
            previous_avg = sum(monthly_sales[-6:-3]) / 3 if len(monthly_sales) >= 6 else recent_avg
            growth_rate = ((recent_avg - previous_avg) / previous_avg * 100) if previous_avg > 0 else 0
        else:
            recent_avg = sum(monthly_sales) / len(monthly_sales)
            growth_rate = 0

        trend = "上升" if growth_rate > 5 else ("下降" if growth_rate < -5 else "稳定")

        return {
            "task": "销售趋势分析",
            "data_points": len(historical_data),
            "recent_3month_avg": round(recent_avg, 2),
            "growth_rate": round(growth_rate, 2),
            "trend_direction": trend,
            "peak_month": max(historical_data, key=lambda x: x.get("sales_amount", 0)).get("month"),
            "lowest_month": min(historical_data, key=lambda x: x.get("sales_amount", 0)).get("month")
        }

    def customer_conversion_prediction(self, customer_data: dict) -> dict:
        """客户转化预测"""
        interaction_score = self._calculate_interaction_score(customer_data.get("interactions", []))
        engagement_score = self._calculate_engagement_score(customer_data.get("engagement_metrics", {}))
        purchase_history_score = self._calculate_purchase_history_score(customer_data.get("purchase_history", []))

        total_score = (interaction_score * 0.3 + engagement_score * 0.4 + purchase_history_score * 0.3)

        if total_score >= 80:
            conversion_probability = "高 (>70%)"
            recommended_action = "立即跟进，提供个性化优惠"
            priority = "高"
        elif total_score >= 60:
            conversion_probability = "中 (50-70%)"
            recommended_action = "持续培育，定期推送相关内容"
            priority = "中"
        elif total_score >= 40:
            conversion_probability = "低 (30-50%)"
            recommended_action = "增加互动，了解需求痛点"
            priority = "低"
        else:
            conversion_probability = "很低 (<30%)"
            recommended_action="重新评估客户匹配度或调整策略"
            priority = "很低"

        return {
            "task": "客户转化预测",
            "customer_id": customer_data.get("customer_id"),
            "total_score": round(total_score, 2),
            "conversion_probability": conversion_probability,
            "recommended_action": recommended_action,
            "priority": priority,
            "score_breakdown": {
                "interaction_score": round(interaction_score, 2),
                "engagement_score": round(engagement_score, 2),
                "purchase_history_score": round(purchase_history_score, 2)
            }
        }

    def _calculate_interaction_score(self, interactions: list) -> float:
        if not interactions:
            return 30.0

        score = 50.0
        recent_interactions = [i for i in interactions if datetime.strptime(i.get("date", "2024-01-01"), "%Y-%m-%d") > datetime.now() - timedelta(days=30)]
        score += len(recent_interactions) * 5

        has_meeting = any(i.get("type") == "meeting" for i in interactions)
        if has_meeting:
            score += 20

        return min(score, 100)

    def _calculate_engagement_score(self, metrics: dict) -> float:
        if not metrics:
            return 40.0

        score = 0
        email_open_rate = metrics.get("email_open_rate", 0)
        website_visits = metrics.get("website_visits", 0)
        content_downloads = metrics.get("content_downloads", 0)

        score += min(email_open_rate * 2, 30)
        score += min(website_visits * 0.5, 30)
        score += min(content_downloads * 10, 40)

        return min(score, 100)

    def _calculate_purchase_history_score(self, history: list) -> float:
        if not history:
            return 20.0

        total_purchases = sum(h.get("amount", 0) for h in history)
        frequency = len(history)

        score = min(frequency * 15, 50)
        score += min(total_purchases / 10000 * 20, 50)

        return min(score, 100)

def model_inference(input_data: dict) -> dict:
    engine = SalesInferenceEngine()
    task_type = input_data.get("task")

    if task_type == "sales_trend_analysis":
        return engine.sales_trend_analysis(input_data.get("historical_data", []))
    elif task_type == "customer_conversion_prediction":
        return engine.customer_conversion_prediction(input_data.get("customer_data", {}))
    else:
        return {"error": f"未知任务类型: {task_type}"}

if __name__ == "__main__":
    data_dir = os.environ.get("DATA_DIR", "/workspace/data")
    print(f"[Sales AI] 启动销售管理智能推理服务，数据目录: {data_dir}")

    for fname in os.listdir(data_dir):
        if fname.endswith('.json'):
            with open(os.path.join(data_dir, fname), 'r', encoding='utf-8') as f:
                input_data = json.load(f)
            result = model_inference(input_data)
            print(json.dumps(result, ensure_ascii=False, indent=2))
