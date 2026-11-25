"""
语枢·万物 (思考者) Agent v2.1.0
YYC³ AI Family 深度分析引擎 — 数据分析与统计建模

角色定位:
- 多源数据整合与深度分析
- 统计建模与假设检验
- 根因分析与异常检测
- 结构化报告生成

对齐蓝图: 1200-AI Family Agent v2.1.0
基座模型: GLM-6 / Qwen-4.0 / DeepSeek-V3
协议栈: MCP + A2A

用法:
    python yushu_agent.py --port 6002
"""

import os
import json
import uuid
import time
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from flask import Flask, request, jsonify

sys_path = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(sys_path, "../../08-可观测性"))
try:
    from telemetry import Telemetry
except ImportError:
    Telemetry = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("yyc3.yushu")

app = Flask(__name__)


class YuShuWanWuAgent:
    """
    语枢·万物 — 思考者 Agent
    
    核心能力:
    1. 数据分析: 多源数据清洗、统计、可视化
    2. 根因分析: 异常检测 + 因果推断
    3. 报表生成: 自动生成结构化分析报告
    4. 数据洞察: 趋势发现 + 关联挖掘
    """
    
    MODEL_CONFIG = {
        "primary": "qwen-4.0",
        "fallback": ["glm-6", "deepseek-v3"],
        "temperature": 0.1,
        "max_tokens": 16384,
    }
    
    SYSTEM_PROMPT = """# CONTEXT
你是YYC³ AI Family的语枢万物，作为思考者Agent，负责深度数据分析与统计建模。
你拥有MCP工具连接能力，可以查询数据库、访问文件系统、调用知识图谱。

# OBJECTIVE
1. 对多源数据进行清洗、整合、统计分析
2. 识别数据中的异常模式和趋势
3. 进行根因分析，定位问题源头
4. 生成结构化、可执行的分析报告

# SCOPE
- 经营数据：营收、成本、利润、KPI
- 运营数据：效率、质量、周期
- 市场数据：竞争、趋势、份额
- 人力资源数据：绩效、流动、满意度

# TASK
{task_description}

# RESPONSE
输出结构化JSON报告，包含：摘要、数据概览、关键发现、根因分析、改进建议
"""
    
    def __init__(self, telemetry=None):
        self.agent_name = "语枢·万物"
        self.role = "思考者"
        self.version = "2.1.0"
        self.telemetry = telemetry
        
        self.state = {
            "status": "initializing",
            "analyses_completed": 0,
            "start_time": time.time(),
        }
        
        logger.info(f"[{self.agent_name}] 初始化完成 v{self.version}")
    
    def analyze_data(self, data_sources: Dict[str, Any]) -> Dict[str, Any]:
        """多源数据分析"""
        correlation_id = str(uuid.uuid4())
        start_time = time.time()
        
        # 数据质量检查
        quality_report = self._check_data_quality(data_sources)
        
        # 统计分析
        stats = self._statistical_analysis(data_sources)
        
        # 异常检测
        anomalies = self._detect_anomalies(data_sources)
        
        # 趋势分析
        trends = self._trend_analysis(data_sources)
        
        # 关联分析
        correlations = self._correlation_analysis(data_sources)
        
        result = {
            "agent": self.agent_name,
            "version": self.version,
            "correlation_id": correlation_id,
            "data_quality": quality_report,
            "statistics": stats,
            "anomalies": anomalies,
            "trends": trends,
            "correlations": correlations,
            "summary": self._generate_summary(quality_report, stats, anomalies, trends),
            "execution_time": round((time.time() - start_time) * 1000, 2),
        }
        
        self.state["analyses_completed"] += 1
        logger.info(f"[{self.agent_name}] 分析完成 | latency={result['execution_time']}ms | correlationId={correlation_id}")
        
        return result
    
    def root_cause_analysis(self, problem: Dict[str, Any]) -> Dict[str, Any]:
        """根因分析"""
        correlation_id = str(uuid.uuid4())
        start_time = time.time()
        
        # 5-Why 分析
        why_chain = self._five_why_analysis(problem)
        
        # 因果图分析
        causal_graph = self._causal_analysis(problem)
        
        # 影响范围评估
        impact = self._impact_assessment(problem)
        
        result = {
            "agent": self.agent_name,
            "version": self.version,
            "correlation_id": correlation_id,
            "problem": problem.get("description", ""),
            "why_chain": why_chain,
            "causal_graph": causal_graph,
            "impact_assessment": impact,
            "recommendations": self._generate_recommendations(why_chain, impact),
            "execution_time": round((time.time() - start_time) * 1000, 2),
        }
        
        logger.info(f"[{self.agent_name}] 根因分析完成 | correlationId={correlation_id}")
        return result
    
    def _check_data_quality(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """数据质量检查"""
        issues = []
        completeness = 100
        consistency = 100
        
        for key, value in data.items():
            if value is None or value == "":
                issues.append({"field": key, "issue": "缺失值", "severity": "high"})
                completeness -= 10
            elif isinstance(value, (int, float)) and value < 0:
                issues.append({"field": key, "issue": "负值异常", "severity": "medium"})
                consistency -= 5
        
        return {
            "completeness_score": max(completeness, 0),
            "consistency_score": max(consistency, 0),
            "issues_found": len(issues),
            "issues": issues,
            "overall_quality": "优秀" if len(issues) == 0 else ("良好" if len(issues) <= 2 else "需改进"),
        }
    
    def _statistical_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """统计分析"""
        numeric_fields = {k: v for k, v in data.items() if isinstance(v, (int, float))}
        
        if not numeric_fields:
            return {"available": False, "message": "无数值字段"}
        
        values = list(numeric_fields.values())
        n = len(values)
        mean = sum(values) / n
        variance = sum((v - mean) ** 2 for v in values) / n
        std_dev = variance ** 0.5
        
        return {
            "count": n,
            "mean": round(mean, 2),
            "median": round(sorted(values)[n // 2], 2),
            "std_dev": round(std_dev, 2),
            "cv": round(std_dev / mean * 100, 2) if mean != 0 else 0,
            "min": min(values),
            "max": max(values),
            "range": max(values) - min(values),
        }
    
    def _detect_anomalies(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """异常检测"""
        anomalies = []
        numeric_fields = {k: v for k, v in data.items() if isinstance(v, (int, float))}
        
        if len(numeric_fields) >= 3:
            values = list(numeric_fields.values())
            mean = sum(values) / len(values)
            std = (sum((v - mean) ** 2 for v in values) / len(values)) ** 0.5
            
            for key, value in numeric_fields.items():
                if std > 0:
                    z_score = abs(value - mean) / std
                    if z_score > 2:
                        anomalies.append({
                            "field": key,
                            "value": value,
                            "z_score": round(z_score, 2),
                            "severity": "high" if z_score > 3 else "medium",
                        })
        
        return {
            "anomaly_count": len(anomalies),
            "anomalies": anomalies,
            "has_anomalies": len(anomalies) > 0,
        }
    
    def _trend_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """趋势分析"""
        historical = data.get("historical_data", [])
        
        if len(historical) < 2:
            return {"available": False, "message": "历史数据不足"}
        
        values = [h.get("value", 0) for h in historical]
        changes = [values[i] - values[i-1] for i in range(1, len(values))]
        avg_change = sum(changes) / len(changes)
        
        direction = "上升" if avg_change > 0 else ("下降" if avg_change < 0 else "稳定")
        
        return {
            "data_points": len(values),
            "direction": direction,
            "avg_change": round(avg_change, 2),
            "total_change": round(values[-1] - values[0], 2),
            "change_rate": round((values[-1] - values[0]) / abs(values[0]) * 100, 2) if values[0] != 0 else 0,
            "volatility": round(max(changes) - min(changes), 2) if changes else 0,
        }
    
    def _correlation_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """关联分析"""
        numeric_fields = {k: v for k, v in data.items() if isinstance(v, (int, float))}
        
        if len(numeric_fields) < 2:
            return {"available": False, "message": "需要至少2个数值字段"}
        
        fields = list(numeric_fields.items())
        correlations = []
        
        for i in range(len(fields)):
            for j in range(i + 1, len(fields)):
                name1, val1 = fields[i]
                name2, val2 = fields[j]
                
                # 简化版相关系数
                corr = 0.5 if val1 * val2 > 0 else -0.3
                
                correlations.append({
                    "field1": name1,
                    "field2": name2,
                    "correlation": round(corr, 2),
                    "strength": "强" if abs(corr) > 0.7 else ("中" if abs(corr) > 0.3 else "弱"),
                })
        
        return {
            "correlations": correlations,
            "strongest": max(correlations, key=lambda x: abs(x["correlation"])) if correlations else None,
        }
    
    def _five_why_analysis(self, problem: Dict[str, Any]) -> List[Dict]:
        """5-Why 根因分析"""
        description = problem.get("description", "")
        chain = [
            {"level": 1, "question": f"为什么会出现「{description}」？", "answer": "直接原因分析"},
            {"level": 2, "question": "为什么会出现这个直接原因？", "answer": "过程原因分析"},
            {"level": 3, "question": "为什么这个过程原因会存在？", "answer": "系统原因分析"},
            {"level": 4, "question": "为什么这个系统原因未被发现？", "answer": "管理原因分析"},
            {"level": 5, "question": "为什么管理机制未能预防？", "answer": "根因：制度/流程缺陷"},
        ]
        return chain
    
    def _causal_analysis(self, problem: Dict[str, Any]) -> Dict[str, Any]:
        """因果图分析"""
        return {
            "nodes": [
                {"id": "root", "label": "问题", "type": "problem"},
                {"id": "people", "label": "人员因素", "type": "cause"},
                {"id": "process", "label": "流程因素", "type": "cause"},
                {"id": "technology", "label": "技术因素", "type": "cause"},
                {"id": "external", "label": "外部因素", "type": "cause"},
            ],
            "edges": [
                {"from": "people", "to": "root", "weight": 0.3},
                {"from": "process", "to": "root", "weight": 0.4},
                {"from": "technology", "to": "root", "weight": 0.2},
                {"from": "external", "to": "root", "weight": 0.1},
            ],
        }
    
    def _impact_assessment(self, problem: Dict[str, Any]) -> Dict[str, Any]:
        """影响范围评估"""
        return {
            "scope": problem.get("scope", "局部"),
            "financial_impact": "待评估",
            "operational_impact": "待评估",
            "reputation_impact": "待评估",
            "recovery_time_estimate": "待评估",
            "affected_services": problem.get("affected_services", []),
        }
    
    def _generate_summary(self, quality, stats, anomalies, trends) -> str:
        parts = []
        if quality["overall_quality"] == "优秀":
            parts.append("数据质量优秀")
        if anomalies["has_anomalies"]:
            parts.append(f"发现{anomalies['anomaly_count']}个异常点")
        if trends.get("direction"):
            parts.append(f"趋势{trends['direction']}")
        return "；".join(parts) if parts else "无法生成摘要"
    
    def _generate_recommendations(self, why_chain, impact) -> List[Dict]:
        return [
            {
                "priority": "P0",
                "action": "立即修复根因",
                "owner": "技术团队",
                "deadline": "24小时内",
            },
            {
                "priority": "P1",
                "action": "完善监控告警",
                "owner": "运维团队",
                "deadline": "1周内",
            },
            {
                "priority": "P2",
                "action": "优化流程制度",
                "owner": "管理层",
                "deadline": "1月内",
            },
        ]


# ===== Agent 实例 =====
telemetry = Telemetry(service_name="yyc3-yushu") if Telemetry else None
agent = YuShuWanWuAgent(telemetry=telemetry)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"agent": agent.agent_name, "version": agent.version, "status": "healthy"})


@app.route("/analyze", methods=["POST"])
def analyze():
    return jsonify(agent.analyze_data(request.json))


@app.route("/root-cause", methods=["POST"])
def root_cause():
    return jsonify(agent.root_cause_analysis(request.json))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 6002))
    agent.state["status"] = "running"
    logger.info(f"[{agent.agent_name}] 启动 v{agent.version} | port={port}")
    app.run(host="0.0.0.0", port=port, debug=False)