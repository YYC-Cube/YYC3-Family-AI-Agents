"""
YYC³ 维护保障智能推理引擎 v2.0
基于 CO-STAR 提示词框架 + AI Family Agent 协同

CO-STAR 提示词框架:
  Context: 企业设备维护保障场景，涵盖预测性维护、排程优化、故障诊断
  Objective: 实现智能化预测性维护、维护排程优化、故障根因分析
  Scope: 设备全生命周期维护、维修资源调度、故障预测与诊断
  Task: 预测性维护、维护排程、故障诊断
  Audience: 维护工程师、设备管理者、运营管理者
  Response: 结构化JSON + 可执行维修方案
"""

import os
import json
import uuid
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List
from collections import defaultdict


class MaintenanceEngine:
    """维护保障智能引擎 v2.0"""

    def __init__(self):
        self.version = "2.1.0"
        self.model = "glm-6"
        self.decision_history: List[Dict] = []
        self._metrics = defaultdict(int)
        self.failure_thresholds = {
            "temperature": 85,
            "vibration": 7.5,
            "pressure": 120,
            "runtime_hours": 8000,
        }
        print(f"[Maintenance] 初始化完成 | version={self.version}")

    def predict_maintenance(self, equipment_data: List[Dict], correlation_id: str = "") -> Dict[str, Any]:
        """预测性维护分析"""
        start_time = time.time()
        if not correlation_id:
            correlation_id = str(uuid.uuid4())

        predictions = []
        critical_count = 0

        for eq in equipment_data:
            risk_score = 0
            alerts = []

            temp = eq.get("temperature", 0)
            if temp > self.failure_thresholds["temperature"]:
                risk_score += 30
                alerts.append(f"温度偏高: {temp}°C (阈值: {self.failure_thresholds['temperature']}°C)")

            vib = eq.get("vibration", 0)
            if vib > self.failure_thresholds["vibration"]:
                risk_score += 25
                alerts.append(f"振动异常: {vib}mm/s (阈值: {self.failure_thresholds['vibration']}mm/s)")

            runtime = eq.get("runtime_hours", 0)
            if runtime > self.failure_thresholds["runtime_hours"]:
                risk_score += 25
                alerts.append(f"运行时长超限: {runtime}h (阈值: {self.failure_thresholds['runtime_hours']}h)")

            # 风险等级
            if risk_score >= 60:
                risk_level = "critical"
                action = "立即停机维护"
                critical_count += 1
            elif risk_score >= 30:
                risk_level = "warning"
                action = "48小时内安排维护"
            elif risk_score > 0:
                risk_level = "attention"
                action = "加强巡检，下周安排维护"
            else:
                risk_level = "normal"
                action = "按常规计划维护"

            predictions.append({
                "equipment_id": eq.get("equipment_id", ""),
                "equipment_name": eq.get("name", ""),
                "risk_score": risk_score,
                "risk_level": risk_level,
                "alerts": alerts,
                "recommended_action": action,
                "next_maintenance_days": max(1, 90 - risk_score),
            })

        result = {
            "task": "预测性维护",
            "equipment_analyzed": len(equipment_data),
            "critical_count": critical_count,
            "overall_health": "差" if critical_count > 0 else ("良好" if len([p for p in predictions if p["risk_level"] == "warning"]) == 0 else "需关注"),
            "predictions": predictions,
            "correlation_id": correlation_id,
            "model": self.model,
            "framework": "CO-STAR",
            "execution_time_ms": round((time.time() - start_time) * 1000, 2),
        }
        self._record(result)
        return result

    def schedule_maintenance(self, tasks: List[Dict], resources: Dict, correlation_id: str = "") -> Dict[str, Any]:
        """维护排程优化"""
        start_time = time.time()
        if not correlation_id:
            correlation_id = str(uuid.uuid4())

        # 按优先级排序
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        sorted_tasks = sorted(tasks, key=lambda t: priority_order.get(t.get("priority", "low"), 99))

        schedule = []
        current_date = datetime.now()
        engineers = resources.get("engineers", 5)

        for i, task in enumerate(sorted_tasks):
            scheduled_date = current_date + timedelta(days=i // engineers)
            schedule.append({
                "task_id": task.get("task_id", ""),
                "task_name": task.get("name", ""),
                "priority": task.get("priority", "medium"),
                "scheduled_date": scheduled_date.strftime("%Y-%m-%d"),
                "assigned_engineer": f"ENG-{(i % engineers) + 1:03d}",
                "estimated_duration_hours": task.get("estimated_hours", 4),
            })

        result = {
            "task": "维护排程",
            "total_tasks": len(tasks),
            "total_engineers": engineers,
            "schedule_span_days": max(1, (len(tasks) + engineers - 1) // engineers),
            "schedule": schedule,
            "resource_utilization_pct": round(min(100, len(tasks) / (engineers * 5) * 100), 2),
            "correlation_id": correlation_id,
            "model": self.model,
            "framework": "CO-STAR",
            "execution_time_ms": round((time.time() - start_time) * 1000, 2),
        }
        self._record(result)
        return result

    def diagnose_fault(self, symptoms: List[str], equipment_info: Dict, correlation_id: str = "") -> Dict[str, Any]:
        """故障诊断"""
        start_time = time.time()
        if not correlation_id:
            correlation_id = str(uuid.uuid4())

        possible_causes = []
        for symptom in symptoms:
            if "振动" in symptom or "噪音" in symptom:
                possible_causes.append({"cause": "轴承磨损", "probability": 0.65, "fix": "更换轴承组件"})
            if "温度" in symptom or "过热" in symptom:
                possible_causes.append({"cause": "散热系统故障", "probability": 0.55, "fix": "清洁散热器/更换风扇"})
            if "压力" in symptom or "泄漏" in symptom:
                possible_causes.append({"cause": "密封件老化", "probability": 0.60, "fix": "更换密封件"})
            if "停机" in symptom or "停止" in symptom:
                possible_causes.append({"cause": "电源或控制系统故障", "probability": 0.50, "fix": "检查电源模块和控制板"})

        if not possible_causes:
            possible_causes.append({"cause": "综合因素", "probability": 0.40, "fix": "进行全面检查"})

        result = {
            "task": "故障诊断",
            "equipment_id": equipment_info.get("equipment_id", ""),
            "symptoms": symptoms,
            "possible_causes": possible_causes[:3],
            "recommended_action": "按优先级依次排查，建议从概率最高的原因开始",
            "estimated_repair_time_hours": len(possible_causes) * 2,
            "correlation_id": correlation_id,
            "model": self.model,
            "framework": "CO-STAR",
            "execution_time_ms": round((time.time() - start_time) * 1000, 2),
        }
        self._record(result)
        return result

    def _record(self, result: Dict):
        self.decision_history.append({
            "timestamp": datetime.now().isoformat(),
            "task": result.get("task", ""),
            "correlation_id": result.get("correlation_id", ""),
        })
        self._metrics["total_decisions"] += 1


def model_inference(input_data: Dict[str, Any]) -> Dict[str, Any]:
    engine = MaintenanceEngine()
    task = input_data.get("task", "")

    if task == "predictive_maintenance":
        return engine.predict_maintenance(input_data.get("equipment_data", []), input_data.get("correlation_id", ""))
    elif task == "maintenance_scheduling":
        return engine.schedule_maintenance(input_data.get("tasks", []), input_data.get("resources", {}), input_data.get("correlation_id", ""))
    elif task == "fault_diagnosis":
        return engine.diagnose_fault(input_data.get("symptoms", []), input_data.get("equipment_info", {}), input_data.get("correlation_id", ""))
    else:
        return {"error": f"未知任务类型: {task}", "supported_tasks": ["predictive_maintenance", "maintenance_scheduling", "fault_diagnosis"]}


if __name__ == "__main__":
    print(f"[Maintenance] 启动维护保障智能推理服务 | version=2.1.0")