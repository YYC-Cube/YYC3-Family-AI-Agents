"""
预见·先知 (预言家) Agent v2.1.0
YYC³ AI Family 预测引擎 — 趋势预测与风险预警

角色定位:
- 时序预测与情景模拟
- 多维度风险识别与预警
- 早期信号检测
- 决策支持与情景规划

对齐蓝图: 1200-AI Family Agent v2.1.0
基座模型: GLM-6 / Qwen-4.0 / DeepSeek-V3

用法:
    python yujian_agent.py --port 6003
"""

import os, json, uuid, time, logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from flask import Flask, request, jsonify

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../08-可观测性"))
try:
    from telemetry import Telemetry
except ImportError:
    Telemetry = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("yyc3.yujian")
app = Flask(__name__)


class YuJianXianZhiAgent:
    """预见·先知 — 预言家 Agent"""
    
    MODEL_CONFIG = {
        "primary": "deepseek-v3",
        "fallback": ["glm-6", "qwen-4.0"],
        "temperature": 0.2,
        "max_tokens": 8192,
    }
    
    def __init__(self, telemetry=None):
        self.agent_name = "预见·先知"
        self.role = "预言家"
        self.version = "2.1.0"
        self.telemetry = telemetry
        self.state = {"status": "initializing", "predictions_made": 0, "start_time": time.time()}
        logger.info(f"[{self.agent_name}] 初始化完成 v{self.version}")
    
    def forecast(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """趋势预测"""
        correlation_id = str(uuid.uuid4())
        start = time.time()
        
        historical = data.get("historical_data", [])
        horizon = data.get("forecast_horizon", 3)
        method = data.get("method", "ensemble")
        
        # 多模型集成预测
        linear_pred = self._linear_forecast(historical, horizon)
        seasonal_pred = self._seasonal_forecast(historical, horizon)
        ensemble_pred = self._ensemble_forecast([linear_pred, seasonal_pred])
        
        result = {
            "agent": self.agent_name, "version": self.version,
            "correlation_id": correlation_id,
            "forecast_horizon": horizon,
            "methods": {
                "linear": linear_pred,
                "seasonal": seasonal_pred,
                "ensemble": ensemble_pred,
            },
            "confidence_intervals": self._confidence_intervals(ensemble_pred),
            "scenario_analysis": self._scenario_analysis(historical, horizon),
            "execution_time": round((time.time() - start) * 1000, 2),
        }
        
        self.state["predictions_made"] += 1
        logger.info(f"[{self.agent_name}] 预测完成 | horizon={horizon} | correlationId={correlation_id}")
        return result
    
    def risk_assessment(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """风险评估"""
        correlation_id = str(uuid.uuid4())
        start = time.time()
        
        risks = []
        
        # 财务风险
        if data.get("financial", {}).get("debt_ratio", 0) > 0.6:
            risks.append({"category": "财务风险", "level": "高", "indicator": "负债率", "value": data["financial"]["debt_ratio"]})
        
        # 运营风险
        if data.get("operational", {}).get("efficiency", 100) < 60:
            risks.append({"category": "运营风险", "level": "中", "indicator": "运营效率", "value": data["operational"]["efficiency"]})
        
        # 市场风险
        if data.get("market", {}).get("volatility", 0) > 0.3:
            risks.append({"category": "市场风险", "level": "高", "indicator": "市场波动", "value": data["market"]["volatility"]})
        
        # 合规风险
        if data.get("compliance", {}).get("violations", 0) > 0:
            risks.append({"category": "合规风险", "level": "极高", "indicator": "合规违规", "value": data["compliance"]["violations"]})
        
        overall = "高" if any(r["level"] in ("极高", "高") for r in risks) else ("中" if risks else "低")
        
        result = {
            "agent": self.agent_name, "version": self.version,
            "correlation_id": correlation_id,
            "overall_risk": overall,
            "risks": risks,
            "risk_count": len(risks),
            "early_warnings": self._early_warnings(risks),
            "execution_time": round((time.time() - start) * 1000, 2),
        }
        
        logger.info(f"[{self.agent_name}] 风险评估完成 | risk={overall} | correlationId={correlation_id}")
        return result
    
    def anomaly_detection(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """异常检测"""
        correlation_id = str(uuid.uuid4())
        start = time.time()
        
        metrics = data.get("metrics", [])
        anomalies = []
        
        for metric in metrics:
            values = [m.get("value", 0) for m in metric.get("data", [])]
            if len(values) >= 3:
                mean = sum(values) / len(values)
                std = (sum((v - mean) ** 2 for v in values) / len(values)) ** 0.5
                for i, v in enumerate(values):
                    if std > 0 and abs(v - mean) > 2.5 * std:
                        anomalies.append({
                            "metric": metric.get("name", "unknown"),
                            "point": i,
                            "value": v,
                            "expected": round(mean, 2),
                            "deviation": round(v - mean, 2),
                            "z_score": round(abs(v - mean) / std, 2),
                        })
        
        result = {
            "agent": self.agent_name, "version": self.version,
            "correlation_id": correlation_id,
            "anomaly_count": len(anomalies),
            "anomalies": anomalies,
            "execution_time": round((time.time() - start) * 1000, 2),
        }
        return result
    
    def _linear_forecast(self, historical: List[Dict], horizon: int) -> List[float]:
        values = [h.get("value", 0) for h in historical]
        if len(values) < 2:
            return [values[-1]] * horizon if values else [0] * horizon
        
        n = len(values)
        x_mean = (n - 1) / 2
        y_mean = sum(values) / n
        slope = sum((i - x_mean) * (values[i] - y_mean) for i in range(n)) / sum((i - x_mean) ** 2 for i in range(n))
        intercept = y_mean - slope * x_mean
        
        return [round(intercept + slope * (n + i), 2) for i in range(horizon)]
    
    def _seasonal_forecast(self, historical: List[Dict], horizon: int) -> List[float]:
        values = [h.get("value", 0) for h in historical]
        if len(values) < 4:
            return self._linear_forecast(historical, horizon)
        
        period = min(4, len(values) // 2)
        seasonal_factors = []
        for i in range(period):
            period_vals = [values[j] for j in range(i, len(values), period)]
            if period_vals:
                seasonal_factors.append(sum(period_vals) / len(period_vals))
        
        avg = sum(seasonal_factors) / len(seasonal_factors)
        seasonal_factors = [s / avg for s in seasonal_factors] if avg > 0 else [1] * len(seasonal_factors)
        
        trend = self._linear_forecast(historical, horizon)
        return [round(trend[i] * seasonal_factors[i % len(seasonal_factors)], 2) for i in range(horizon)]
    
    def _ensemble_forecast(self, predictions: List[List[float]]) -> List[float]:
        if not predictions:
            return []
        return [round(sum(p[i] for p in predictions) / len(predictions), 2) for i in range(len(predictions[0]))]
    
    def _confidence_intervals(self, forecast: List[float]) -> Dict[str, List[float]]:
        return {
            "lower_bound": [round(f * 0.9, 2) for f in forecast],
            "upper_bound": [round(f * 1.1, 2) for f in forecast],
        }
    
    def _scenario_analysis(self, historical: List[Dict], horizon: int) -> Dict[str, Any]:
        base = self._ensemble_forecast([self._linear_forecast(historical, horizon), self._seasonal_forecast(historical, horizon)])
        return {
            "optimistic": {"values": [round(b * 1.15, 2) for b in base], "probability": 0.25, "trigger": "有利政策/市场扩张"},
            "baseline": {"values": base, "probability": 0.50, "trigger": "当前趋势延续"},
            "pessimistic": {"values": [round(b * 0.85, 2) for b in base], "probability": 0.25, "trigger": "不利外部冲击"},
        }
    
    def _early_warnings(self, risks: List[Dict]) -> List[Dict]:
        warnings = []
        for r in risks:
            if r["level"] in ("极高", "高"):
                warnings.append({"risk": r["category"], "action": f"立即关注{r['indicator']}指标", "urgency": "immediate"})
        return warnings


telemetry = Telemetry(service_name="yyc3-yujian") if Telemetry else None
agent = YuJianXianZhiAgent(telemetry=telemetry)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"agent": agent.agent_name, "version": agent.version, "status": "healthy"})


@app.route("/forecast", methods=["POST"])
def forecast():
    return jsonify(agent.forecast(request.json))


@app.route("/risk-assessment", methods=["POST"])
def risk_assessment():
    return jsonify(agent.risk_assessment(request.json))


@app.route("/anomaly", methods=["POST"])
def anomaly():
    return jsonify(agent.anomaly_detection(request.json))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 6003))
    agent.state["status"] = "running"
    logger.info(f"[{agent.agent_name}] 启动 v{agent.version} | port={port}")
    app.run(host="0.0.0.0", port=port, debug=False)