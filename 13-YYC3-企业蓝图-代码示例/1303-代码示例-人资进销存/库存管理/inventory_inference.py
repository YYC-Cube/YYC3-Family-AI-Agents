import os
import json

class InventoryInferenceEngine:
    def __init__(self):
        self.safety_stock_factor = 1.5
        self.reorder_point_factor = 2.0

    def inventory_prediction(self, inventory_data: dict) -> dict:
        """智能库存预测"""
        current_stock = inventory_data.get("current_stock", 0)
        daily_demand_avg = inventory_data.get("daily_demand_avg", 0)
        lead_time_days = inventory_data.get("lead_time_days", 7)
        demand_variance = inventory_data.get("demand_variance", 10)

        safety_stock = int(daily_demand_avg * lead_time_days * self.safety_stock_factor)
        reorder_point = int(daily_demand_avg * lead_time_days * self.reorder_point_factor)

        days_of_stock = current_stock / daily_demand_avg if daily_demand_avg > 0 else float('inf')

        if current_stock <= safety_stock:
            status = "库存不足"
            urgency = "紧急"
            action = "立即补货"
        elif current_stock <= reorder_point:
            status = "接近补货点"
            urgency = "高"
            action = "建议尽快补货"
        elif current_stock > reorder_point * 1.5:
            status = "库存充足"
            urgency = "低"
            action = "正常监控"
        else:
            status = "库存正常"
            urgency = "中"
            action = "持续监控"

        return {
            "task": "库存预测",
            "product_id": inventory_data.get("product_id"),
            "current_stock": current_stock,
            "days_of_stock": round(days_of_stock, 1),
            "safety_stock": safety_stock,
            "reorder_point": reorder_point,
            "status": status,
            "urgency": urgency,
            "recommended_action": action,
            "predicted_shortage_risk": "高" if days_of_stock < lead_time_days else ("中" if days_of_stock < lead_time_days * 2 else "低")
        }

    def auto_replenishment_recommendation(self, inventory_list: list) -> list:
        """自动补货建议"""
        recommendations = []

        for item in inventory_list:
            prediction = self.inventory_prediction(item)

            if prediction["urgency"] in ["紧急", "高"]:
                recommended_qty = max(
                    prediction["reorder_point"] * 1.5 - item.get("current_stock", 0),
                    item.get("min_order_quantity", 100)
                )
                recommendations.append({
                    "product_id": item.get("product_id"),
                    "priority": prediction["urgency"],
                    "current_stock": item.get("current_stock"),
                    "recommended_order_quantity": int(recommended_qty),
                    "reason": prediction["recommended_action"],
                    "estimated_cost": round(recommended_qty * item.get("unit_cost", 0), 2)
                })

        recommendations.sort(key=lambda x: {"紧急": 0, "高": 1, "中": 2, "低": 3}.get(x["priority"], 4))

        total_replenishment_cost = sum(r["estimated_cost"] for r in recommendations)

        return {
            "task": "补货建议",
            "total_items_needing_replenishment": len(recommendations),
            "total_estimated_cost": round(total_replenishment_cost, 2),
            "recommendations": recommendations[:10],
            "summary": {
                "urgent_count": len([r for r in recommendations if r["priority"] == "紧急"]),
                "high_priority_count": len([r for r in recommendations if r["priority"] == "高"])
            }
        }

def model_inference(input_data: dict) -> dict:
    engine = InventoryInferenceEngine()
    task_type = input_data.get("task")

    if task_type == "inventory_prediction":
        return engine.inventory_prediction(input_data.get("inventory_data", {}))
    elif task_type == "auto_replenishment":
        return engine.auto_replenishment_recommendation(input_data.get("inventory_list", []))
    else:
        return {"error": f"未知任务类型: {task_type}"}

if __name__ == "__main__":
    data_dir = os.environ.get("DATA_DIR", "/workspace/data")
    print(f"[Inventory AI] 启动库存管理智能推理服务，数据目录: {data_dir}")

    for fname in os.listdir(data_dir):
        if fname.endswith('.json'):
            with open(os.path.join(data_dir, fname), 'r', encoding='utf-8') as f:
                input_data = json.load(f)
            result = model_inference(input_data)
            print(json.dumps(result, ensure_ascii=False, indent=2))
