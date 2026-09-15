import os
import json

class PurchaseInferenceEngine:
    def __init__(self):
        self.supplier_performance_metrics = [
            "delivery_time",
            "quality_score",
            "price_competitiveness",
            "service_responsiveness",
            "reliability"
        ]

    def supplier_evaluation(self, supplier_data: dict) -> dict:
        """智能供应商评估"""
        supplier_id = supplier_data.get("supplier_id")
        performance_history = supplier_data.get("performance_history", {})

        scores = []
        for metric in self.supplier_performance_metrics:
            value = performance_history.get(metric, 0)
            normalized_score = min(value * 20, 100)
            scores.append({
                "metric": metric,
                "raw_value": value,
                "normalized_score": round(normalized_score, 2)
            })

        avg_score = sum(s["normalized_score"] for s in scores) / len(scores) if scores else 0

        if avg_score >= 80:
            tier = "A类（战略供应商）"
            recommendation = "优先合作，可考虑长期合同"
        elif avg_score >= 60:
            tier = "B类（合格供应商）"
            recommendation = "正常合作，持续监控表现"
        elif avg_score >= 40:
            tier = "C类（待改进供应商）"
            recommendation = "需要改进计划或寻找替代方案"
        else:
            tier = "D类（不合格供应商）"
            recommendation = "建议终止合作"

        return {
            "task": "供应商评估",
            "supplier_id": supplier_id,
            "overall_score": round(avg_score, 2),
            "supplier_tier": tier,
            "recommendation": recommendation,
            "detailed_scores": scores,
            "risk_level": "低" if avg_score >= 70 else ("中" if avg_score >= 50 else "高")
        }

    def procurement_recommendation(self, requirements: list) -> dict:
        """采购决策建议"""
        recommendations = []
        total_estimated_cost = 0

        for req in requirements:
            item_name = req.get("item_name")
            quantity = req.get("quantity", 0)
            unit_price = req.get("estimated_unit_price", 0)
            urgency = req.get("urgency", "normal")

            item_total = quantity * unit_price
            total_estimated_cost += item_total

            if urgency == "critical":
                priority = "紧急采购"
                strategy = "立即启动加急采购流程，可接受较高价格"
            elif urgency == "high":
                priority = "高优先级"
                strategy = "优先从A类供应商询价，缩短交货期"
            else:
                priority = "常规采购"
                strategy = "多家比价，优化成本"

            recommendations.append({
                "item": item_name,
                "quantity": quantity,
                "estimated_cost": round(item_total, 2),
                "priority": priority,
                "procurement_strategy": strategy
            })

        return {
            "task": "采购建议",
            "total_items": len(requirements),
            "total_estimated_cost": round(total_estimated_cost, 2),
            "recommendations": recommendations,
            "budget_alert": "超出预算" if total_estimated_cost > requirements[0].get("budget_limit", float('inf')) else "预算内"
        }

def model_inference(input_data: dict) -> dict:
    engine = PurchaseInferenceEngine()
    task_type = input_data.get("task")

    if task_type == "supplier_evaluation":
        return engine.supplier_evaluation(input_data.get("supplier_data", {}))
    elif task_type == "procurement_recommendation":
        return engine.procurement_recommendation(input_data.get("requirements", []))
    else:
        return {"error": f"未知任务类型: {task_type}"}

if __name__ == "__main__":
    data_dir = os.environ.get("DATA_DIR", "/workspace/data")
    print(f"[Purchase AI] 启动采购管理智能推理服务，数据目录: {data_dir}")

    for fname in os.listdir(data_dir):
        if fname.endswith('.json'):
            with open(os.path.join(data_dir, fname), 'r', encoding='utf-8') as f:
                input_data = json.load(f)
            result = model_inference(input_data)
            print(json.dumps(result, ensure_ascii=False, indent=2))
