import os
import json
from datetime import datetime, timedelta

class AssetInferenceEngine:
    def __init__(self):
        self.asset_lifecycle_stages = ["采购", "入库", "使用", "维护", "报废"]

    def asset_tracking(self, asset_info: dict) -> dict:
        """资产全生命周期跟踪"""
        asset_id = asset_info.get("asset_id")
        current_stage = asset_info.get("stage", "采购")
        purchase_date = asset_info.get("purchase_date")
        expected_lifetime = asset_info.get("expected_lifetime_years", 5)

        stage_index = self.asset_lifecycle_stages.index(current_stage) if current_stage in self.asset_lifecycle_stages else 0

        if purchase_date:
            purchase_dt = datetime.strptime(purchase_date, "%Y-%m-%d")
            years_in_use = (datetime.now() - purchase_dt).days / 365.25
            depreciation = min(years_in_use / expected_lifetime, 1.0) * 100
            remaining_value = max(0, (1 - years_in_use / expected_lifetime)) * asset_info.get("original_value", 0)
        else:
            depreciation = 0
            remaining_value = asset_info.get("original_value", 0)
            years_in_use = 0

        return {
            "task": "资产跟踪",
            "asset_id": asset_id,
            "current_stage": current_stage,
            "stage_progress": f"{stage_index + 1}/{len(self.asset_lifecycle_stages)}",
            "next_stage": self.asset_lifecycle_stages[stage_index + 1] if stage_index < len(self.asset_lifecycle_stages) - 1 else "生命周期结束",
            "depreciation_rate": round(depreciation, 2),
            "remaining_value": round(remaining_value, 2),
            "years_in_use": round(years_in_use, 2),
            "maintenance_alert": "需要维护" if years_in_use > expected_lifetime * 0.7 else "正常"
        }

    def utilization_analysis(self, assets: list) -> dict:
        """资产使用率分析"""
        total_assets = len(assets)
        active_assets = sum(1 for a in assets if a.get("status") == "active")
        idle_assets = sum(1 for a in assets if a.get("status") == "idle")
        maintenance_assets = sum(1 for a in assets if a.get("status") == "maintenance")

        total_value = sum(a.get("original_value", 0) for a in assets)
        active_value = sum(a.get("original_value", 0) for a in assets if a.get("status") == "active")

        return {
            "task": "资产利用率分析",
            "total_assets": total_assets,
            "active_count": active_assets,
            "idle_count": idle_assets,
            "maintenance_count": maintenance_assets,
            "utilization_rate": round(active_assets / total_assets * 100, 2) if total_assets > 0 else 0,
            "total_asset_value": round(total_value, 2),
            "active_asset_value": round(active_value, 2),
            "value_utilization": round(active_value / total_value * 100, 2) if total_value > 0 else 0,
            "optimization_suggestions": self._generate_optimization_suggestions(active_assets, idle_assets, total_assets)
        }

    def _generate_optimization_suggestions(self, active: int, idle: int, total: int) -> list:
        suggestions = []
        idle_rate = idle / total if total > 0 else 0

        if idle_rate > 0.3:
            suggestions.append({"type": "warning", "message": f"闲置资产比例过高 ({idle_rate*100:.1f}%)，建议重新分配或处置"})
        if idle_rate > 0.5:
            suggestions.append({"type": "critical", "message": "严重资产闲置，需立即进行资产盘点和优化"})

        if len(suggestions) == 0:
            suggestions.append({"type": "info", "message": "资产利用率良好"})

        return suggestions

def model_inference(input_data: dict) -> dict:
    engine = AssetInferenceEngine()
    task_type = input_data.get("task")

    if task_type == "asset_tracking":
        return engine.asset_tracking(input_data.get("asset_info", {}))
    elif task_type == "utilization_analysis":
        return engine.utilization_analysis(input_data.get("assets", []))
    else:
        return {"error": f"未知任务类型: {task_type}"}

if __name__ == "__main__":
    data_dir = os.environ.get("DATA_DIR", "/workspace/data")
    print(f"[Asset AI] 启动资产管理智能推理服务，数据目录: {data_dir}")

    for fname in os.listdir(data_dir):
        if fname.endswith('.json'):
            with open(os.path.join(data_dir, fname), 'r', encoding='utf-8') as f:
                input_data = json.load(f)
            result = model_inference(input_data)
            print(json.dumps(result, ensure_ascii=False, indent=2))
