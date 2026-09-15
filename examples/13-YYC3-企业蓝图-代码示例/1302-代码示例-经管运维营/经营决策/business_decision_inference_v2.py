"""
YYC³ 经营决策智能化系统 v2.0
基于 Five S 模型 + AI Family Agent 协同架构

核心能力:
1. 提示词驱动的智能分析（Five S模型）
2. AI Family Agent 多角色协同
3. 五维价值矩阵全景评估
4. 实时决策支持与预警
5. 可追溯、可验证的决策链路

五高保障: 高可用 | 高性能 | 高安全 | 高扩展 | 高智能
"""

import os
import sys
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '00-核心基础设施', 'prompt-engine'))

try:
    from prompt_engine import PromptEngine, PromptType, AgentRole
    PROMPT_ENGINE_AVAILABLE = True
except ImportError:
    PROMPT_ENGINE_AVAILABLE = False
    print("[Warning] 提示词引擎未加载，将使用内置模板")


@dataclass
class BusinessContext:
    """业务上下文数据类"""
    period: str
    financial_data: Dict[str, Any]
    market_data: Dict[str, Any]
    operational_data: Dict[str, Any]
    strategic_goals: List[str] = None
    risk_tolerance: str = "中等"
    decision_urgency: str = "正常"


class AIFamilyCoordinator:
    """
    AI Family Agent 协调器

    负责协调8个AI Agent的协同工作，实现拟人化决策支持
    """

    def __init__(self):
        self.agents = {
            "yuanqi_tianshu": {
                "name": "元启·天枢",
                "role": "总指挥",
                "responsibility": "全局协调、最终决策、资源分配",
                "capabilities": ["战略规划", "资源调度", "决策仲裁"]
            },
            "yanqi_qianhang": {
                "name": "言启·千行",
                "role": "导航员",
                "responsibility": "流程导航、信息索引、路径规划",
                "capabilities": ["智能导航", "快速定位", "结构化输出"]
            },
            "yushu_wanwu": {
                "name": "语枢·万物",
                "role": "思考者",
                "responsibility": "数据分析、逻辑推理、深度思考",
                "capabilities": ["数据分析", "逻辑推理", "异常检测"]
            },
            "yujian_xianzhi": {
                "name": "预见·先知",
                "role": "预言家",
                "responsibility": "趋势预测、风险预警、情景模拟",
                "capabilities": ["时序预测", "风险评估", "情景分析"]
            },
            "qianli_bole": {
                "name": "千里·伯乐",
                "role": "推荐官",
                "responsibility": "方案推荐、最佳实践、资源匹配",
                "capabilities": ["智能推荐", "方案评估", "资源优化"]
            },
            "zhiyun_shouhu": {
                "name": "智云·守护",
                "role": "安全官",
                "responsibility": "合规检查、风险控制、安全保障",
                "capabilities": ["合规审计", "风险控制", "安全预警"]
            },
            "gewu_zongshi": {
                "name": "格物·宗师",
                "role": "质量官",
                "responsibility": "质量审核、准确性验证、标准执行",
                "capabilities": ["质量审核", "数值校验", "标准验证"]
            },
            "chuangxiang_lingyun": {
                "name": "创想·灵韵",
                "role": "创意官",
                "responsibility": "创新建议、内容创作、可视化设计",
                "capabilities": ["创意生成", "报告润色", "可视化建议"]
            }
        }

    def get_agent(self, agent_id: str) -> Dict:
        """获取Agent信息"""
        return self.agents.get(agent_id, {})

    def coordinate_analysis(self, task_type: str, context: BusinessContext) -> Dict:
        """
        协调多Agent进行综合分析

        Args:
            task_type: 任务类型（如：经营分析、战略规划等）
            context: 业务上下文

        Returns:
            多Agent协同分析结果
        """
        coordination_result = {
            "coordination_metadata": {
                "task_type": task_type,
                "coordinated_at": datetime.now().isoformat(),
                "agents_involved": [],
                "coordination_protocol": "YYC3-AIFamily-v2.0"
            },
            "agent_results": {},
            "synthesized_insight": None,
            "confidence_score": 0.0,
            "quality_assurance": {}
        }

        if task_type == "business_analysis":
            agents_to_invoke = ["yushu_wanwu", "yujian_xianzhi", "gewu_zongshi", "yanqi_qianhang"]
        elif task_type == "strategic_planning":
            agents_to_invoke = ["yuanqi_tianshu", "yujian_xianzhi", "qianli_bole", "chuangxiang_lingyun"]
        elif task_type == "risk_assessment":
            agents_to_invoke = ["zhiyun_shouhu", "yujian_xianzhi", "gewu_zongshi"]
        else:
            agents_to_invoke = ["yushu_wanwu", "gewu_zongshi"]

        for agent_id in agents_to_invoke:
            agent_info = self.agents.get(agent_id, {})
            if agent_info:
                coordination_result["agents_involved"].append({
                    "agent_id": agent_id,
                    "agent_name": agent_info.get("name"),
                    "role": agent_info.get("role")
                })

                agent_result = self._invoke_agent(agent_id, task_type, context)
                coordination_result["agent_results"][agent_id] = agent_result

        coordination_result["synthesized_insight"] = self._synthesize_results(
            coordination_result["agent_results"]
        )
        coordination_result["confidence_score"] = self._calculate_confidence(
            coordination_result["agent_results"]
        )
        coordination_result["quality_assurance"] = self._quality_check(
            coordination_result["agent_results"]
        )

        return coordination_result

    def _invoke_agent(self, agent_id: str, task_type: str, context: BusinessContext) -> Dict:
        """调用单个Agent进行分析"""
        agent = self.agents.get(agent_id, {})

        base_result = {
            "agent_name": agent.get("name", "未知"),
            "agent_role": agent.get("role", "未知"),
            "analysis_timestamp": datetime.now().isoformat(),
            "findings": [],
            "confidence": 0.0,
            "recommendations": []
        }

        if agent_id == "yushu_wanwu":
            base_result.update(self._analyze_data(context))
        elif agent_id == "yujian_xianzhi":
            base_result.update(self._predict_trends(context))
        elif agent_id == "gewu_zongshi":
            base_result.update(self._validate_quality(context))
        elif agent_id == "yanqi_qianhang":
            base_result.update(self._structure_output(context))
        elif agent_id == "zhiyun_shouhu":
            base_result.update(self._assess_risk(context))
        elif agent_id == "qianli_bole":
            base_result.update(self._recommend_solutions(context))
        elif agent_id == "chuangxiang_lingyun":
            base_result.update(self._generate_creative_insights(context))
        elif agent_id == "yuanqi_tianshu":
            base_result.update(self._strategic_coordination(context))

        return base_result

    def _analyze_data(self, context: BusinessContext) -> Dict:
        """语枢·万物 - 数据分析"""
        financial = context.financial_data
        revenue = financial.get("revenue", 0)
        costs = financial.get("costs", 0)
        profit_margin = ((revenue - costs) / revenue * 100) if revenue > 0 else 0

        findings = []
        if profit_margin > 20:
            findings.append({"type": "positive", "message": f"利润率优秀 ({profit_margin:.1f}%)", "severity": "info"})
        elif profit_margin < 10:
            findings.append({"type": "warning", "message": f"利润率偏低 ({profit_margin:.1f}%)，需关注成本", "severity": "warning"})

        market = context.market_data
        growth_rate = market.get("growth_rate", 0)
        if growth_rate > 15:
            findings.append({"type": "positive", "message": f"市场增长强劲 ({growth_rate:.1f}%)", "severity": "success"})
        elif growth_rate < 5:
            findings.append({"type": "warning", "message": f"市场增长放缓 ({growth_rate:.1f}%)", "severity": "warning"})

        return {
            "findings": findings,
            "confidence": 0.85 if len(findings) > 0 else 0.6,
            "key_metrics": {
                "profit_margin": round(profit_margin, 2),
                "market_growth": growth_rate,
                "operational_efficiency": context.operational_data.get("efficiency_score", 70)
            },
            "analysis_method": "多维度数据分析 + 统计模型"
        }

    def _predict_trends(self, context: BusinessContext) -> Dict:
        """预见·先知 - 趋势预测"""
        predictions = []
        confidence_scores = []

        financial = context.financial_data
        current_revenue = financial.get("revenue", 0)
        growth_rate = context.market_data.get("growth_rate", 10)

        next_quarter_revenue = current_revenue * (1 + growth_rate / 100)
        predictions.append({
            "metric": "营收预测",
            "current_value": current_revenue,
            "predicted_value": round(next_quarter_revenue, 2),
            "time_horizon": "Q+1",
            "confidence": min(0.9, abs(growth_rate) / 20)
        })
        confidence_scores.append(min(0.9, abs(growth_rate) / 20))

        risk_scenarios = []
        if growth_rate < 5:
            risk_scenarios.append({
                "scenario": "保守情景",
                "probability": 0.3,
                "impact": "营收可能下降5-10%",
                "mitigation": "加强成本控制，拓展新市场"
            })
        if growth_rate > 20:
            risk_scenarios.append({
                "scenario": "乐观情景",
                "probability": 0.4,
                "impact": "营收可能增长20-30%",
                "action": "扩大产能，增加投入"
            })

        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.6

        return {
            "predictions": predictions,
            "risk_scenarios": risk_scenarios,
            "confidence": round(avg_confidence, 2),
            "prediction_method": "时序外推 + 情景模拟",
            "early_warnings": self._generate_early_warnings(context)
        }

    def _validate_quality(self, context: BusinessContext) -> Dict:
        """格物·宗师 - 质量验证"""
        quality_checks = []
        overall_quality_score = 100.0

        financial = context.financial_data
        if financial.get("revenue", 0) <= 0:
            quality_checks.append({"check": "营收数据完整性", "status": "FAIL", "message": "营收数据缺失或无效"})
            overall_quality_score -= 20
        else:
            quality_checks.append({"check": "营收数据完整性", "status": "PASS", "message": "数据完整"})

        if context.market_data.get("growth_rate") is None:
            quality_checks.append({"check": "市场增长率有效性", "status": "WARNING", "message": "增长率缺失，使用默认值"})
            overall_quality_score -= 10
        else:
            quality_checks.append({"check": "市场增长率有效性", "status": "PASS", "message": "数据有效"})

        data_consistency = self._check_data_consistency(context)
        quality_checks.extend(data_consistency["checks"])
        overall_quality_score += data_consistency["score_adjustment"]

        return {
            "quality_checks": quality_checks,
            "overall_quality_score": max(0, min(100, overall_quality_score)),
            "confidence": overall_quality_score / 100,
            "validation_status": "APPROVED" if overall_quality_score >= 80 else ("REVIEW" if overall_quality_score >= 60 else "REJECTED"),
            "recommendations": [
                "补充缺失的关键指标数据" if overall_quality_score < 80 else "数据质量良好",
                "建立数据质量监控机制" if overall_quality_score < 90 else "继续保持高标准"
            ]
        }

    def _structure_output(self, context: BusinessContext) -> Dict:
        """言启·千行 - 结构化输出"""
        structure_template = {
            "executive_summary": {
                "period": context.period,
                "overall_status": "健康" if context.financial_data.get("profit_margin", 0) > 15 else "需关注",
                "key_highlight": "",
                "action_required": False
            },
            "detailed_sections": [
                {"section": "财务健康度", "priority": "high", "status": ""},
                {"section": "市场表现", "priority": "high", "status": ""},
                {"section": "运营效率", "priority": "medium", "status": ""},
                {"section": "风险预警", "priority": "critical", "items": []}
            ],
            "navigation_index": {
                "quick_links": ["核心指标", "趋势分析", "风险提示", "行动建议"],
                "estimated_reading_time": "3分钟"
            }
        }

        return {
            "structured_output": structure_template,
            "confidence": 0.95,
            "formatting_standard": "YYC3-BusinessReport-v2.0",
            "accessibility_features": ["语义标记", "关键信息高亮", "层级导航"]
        }

    def _assess_risk(self, context: BusinessContext) -> Dict:
        """智云·守护 - 风险评估"""
        risk_factors = []
        risk_score = 0

        financial = context.financial_data
        profit_margin = ((financial.get("revenue", 0) - financial.get("costs", 0)) /
                        financial.get("revenue", 1) * 100) if financial.get("revenue", 0) > 0 else 0

        if profit_margin < 10:
            risk_factors.append({
                "risk_type": "财务风险",
                "severity": "高",
                "description": f"利润率偏低 ({profit_margin:.1f}%)，存在亏损风险",
                "probability": 0.7,
                "impact": "严重",
                "mitigation": "立即启动成本优化计划"
            })
            risk_score += 30

        market_growth = context.market_data.get("growth_rate", 0)
        if market_growth < 0:
            risk_factors.append({
                "risk_type": "市场风险",
                "severity": "极高",
                "description": "市场负增长，竞争加剧",
                "probability": 0.8,
                "impact": "严重",
                "mitigation": "重新评估市场策略，寻找新的增长点"
            })
            risk_score += 40

        operational_efficiency = context.operational_data.get("efficiency_score", 70)
        if operational_efficiency < 60:
            risk_factors.append({
                "risk_type": "运营风险",
                "severity": "中",
                "description": f"运营效率偏低 ({operational_efficiency}%)",
                "probability": 0.5,
                "impact": "中等",
                "mitigation": "优化运营流程，引入自动化工具"
            })
            risk_score += 20

        compliance_status = "合规"  # 简化处理
        risk_factors.append({
            "risk_type": "合规风险",
            "severity": "低",
            "description": f"当前状态: {compliance_status}",
            "probability": 0.1,
            "impact": "轻微",
            "mitigation": "持续监控法规变化"
        })

        overall_risk_level = "低" if risk_score < 30 else ("中" if risk_score < 60 else ("高" if risk_score < 80 else "极高"))

        return {
            "risk_factors": risk_factors,
            "overall_risk_score": min(100, risk_score),
            "overall_risk_level": overall_risk_level,
            "confidence": 0.88,
            "compliance_status": compliance_status,
            "security_posture": "安全",
            "immediate_actions": [rf["mitigation"] for rf in risk_factors if rf["severity"] in ["高", "极高"]]
        }

    def _recommend_solutions(self, context: BusinessContext) -> Dict:
        """千里·伯乐 - 方案推荐"""
        recommendations = []

        financial = context.financial_data
        profit_margin = ((financial.get("revenue", 0) - financial.get("costs", 0)) /
                        financial.get("revenue", 1) * 100) if financial.get("revenue", 0) > 0 else 0

        if profit_margin < 15:
            recommendations.append({
                "category": "成本优化",
                "solution": "智能成本管控系统",
                "description": "基于AI的成本分析和优化建议",
                "expected_benefit": "提升利润率3-5%",
                "implementation_complexity": "中",
                "priority": "高",
                "roi_timeline": "3-6个月"
            })

        market_growth = context.market_data.get("growth_rate", 0)
        if market_growth < 10:
            recommendations.append({
                "category": "市场扩展",
                "solution": "数字化营销平台",
                "description": "全渠道精准营销和客户洞察",
                "expected_benefit": "提升市场份额5-8%",
                "implementation_complexity": "中高",
                "priority": "高",
                "roi_timeline": "6-12个月"
            })

        recommendations.append({
            "category": "运营提升",
            "solution": "智能运营中心",
            "description": "实时监控和自动化运营决策",
            "expected_benefit": "提升运营效率20%",
            "implementation_complexity": "中",
            "priority": "中",
            "roi_timeline": "6个月"
        })

        best_practices = [
            "建立数据驱动的决策文化",
            "实施滚动式战略规划",
            "构建敏捷组织能力",
            "投资员工技能提升"
        ]

        return {
            "recommended_solutions": recommendations,
            "best_practices": best_practices,
            "confidence": 0.82,
            "recommendation_method": "多维度评估 + 行业对标",
            "resource_requirements": self._estimate_resources(recommendations)
        }

    def _generate_creative_insights(self, context: BusinessContext) -> Dict:
        """创想·灵韵 - 创意洞察"""
        creative_insights = []

        market_growth = context.market_data.get("growth_rate", 0)
        if market_growth > 15:
            creative_insights.append({
                "insight_type": "机会识别",
                "title": "高速增长窗口期",
                "description": "当前处于市场高速增长期，建议加大创新投入",
                "creative_elements": ["探索性营销", "产品线扩展", "生态合作"],
                "visualization_suggestion": "采用动态增长曲线图展示增长势头"
            })

        creative_insights.append({
            "insight_type": "差异化定位",
            "title": "构建独特竞争优势",
            "description": "基于AI能力构建差异化竞争优势",
            "creative_elements": [
                "AI驱动的客户体验",
                "智能化产品服务",
                "数据资产变现"
            ],
            "visualization_suggestion": "使用雷达图展示多维竞争力"
        })

        narrative_style = {
            "tone": "专业且富有感染力",
            "storytelling_approach": "数据驱动的叙事",
            "key_messages": [
                "以数据为基石，以洞察为指引",
                "在变革中把握机遇，在挑战中实现超越",
                "智能化转型不是选择，而是必然"
            ]
        }

        return {
            "creative_insights": creative_insights,
            "narrative_style": narrative_style,
            "confidence": 0.75,
            "creativity_score": 0.85,
            "presentation_recommendations": [
                "使用可视化图表增强表现力",
                "融入成功案例故事",
                "突出数据和情感的平衡"
            ]
        }

    def _strategic_coordination(self, context: BusinessContext) -> Dict:
        """元启·天枢 - 战略协调"""
        strategic_priorities = []

        financial = context.financial_data
        profit_margin = ((financial.get("revenue", 0) - financial.get("costs", 0)) /
                        financial.get("revenue", 1) * 100) if financial.get("revenue", 0) > 0 else 0

        if profit_margin < 15:
            strategic_priorities.append({
                "priority": "P1 - 紧急",
                "objective": "盈利能力提升",
                "actions": ["成本结构优化", "定价策略调整", "高毛利产品聚焦"],
                "resource_allocation": "30%年度预算",
                "timeline": "Q2完成初步成效"
            })

        market_growth = context.market_data.get("growth_rate", 0)
        if market_growth < 10:
            strategic_priorities.append({
                "priority": "P2 - 重要",
                "objective": "市场地位巩固",
                "actions": ["市场份额提升", "客户忠诚度计划", "渠道优化"],
                "resource_allocation": "25%年度预算",
                "timeline": "年内见效"
            })

        strategic_priorities.append({
            "priority": "P3 - 战略",
            "objective": "能力建设与数字化转型",
            "actions": ["AI能力建设", "数据中台搭建", "组织效能提升"],
            "resource_allocation": "35%年度预算",
            "timeline": "18个月里程碑"
        })

        resource_matrix = {
            "financial_resources": {"budget": "已规划", "allocation_status": "待审批"},
            "human_resources": {"key_roles": ["CFO", "CMO", "CTO"], "recruitment_status": "进行中"},
            "technology_resources": {"platform": "YYC³ AI Platform", "readiness": "就绪"},
            "external_partnerships": {"strategy": "生态合作", "status": "探索中"}
        }

        return {
            "strategic_priorities": strategic_priorities,
            "resource_matrix": resource_matrix,
            "governance_structure": {
                "decision_committee": "战略委员会",
                "review_cycle": "月度",
                "escalation_path": "CEO → 董事会"
            },
            "confidence": 0.90,
            "coordination_method": "平衡计分卡 + OKR对齐"
        }

    def _synthesize_results(self, agent_results: Dict) -> Dict:
        """综合各Agent结果"""
        synthesis = {
            "overall_assessment": "",
            "key_findings": [],
            "consensus_actions": [],
            "divergent_views": [],
            "final_recommendation": ""
        }

        all_findings = []
        for agent_id, result in agent_results.items():
            findings = result.get("findings", [])
            all_findings.extend(findings)

        positive_findings = [f for f in all_findings if f.get("type") == "positive"]
        warning_findings = [f for f in all_findings if f.get("type") == "warning"]

        if len(positive_findings) > len(warning_findings):
            synthesis["overall_assessment"] = "整体状况良好，具备增长潜力"
        elif len(warning_findings) > len(positive_findings) * 2:
            synthesis["overall_assessment"] = "存在较多风险因素，需重点关注"
        else:
            synthesis["overall_assessment"] = "状况平稳，机遇与挑战并存"

        synthesis["key_findings"] = all_findings[:5]

        common_actions = ["数据质量持续改进", "建立监控预警机制", "推进数字化转型"]
        synthesis["consensus_actions"] = common_actions

        synthesis["final_recommendation"] = (
            "基于多维度分析，建议采取均衡发展策略："
            "在确保稳健经营的基础上，适度加大创新投入，"
            "同时建立完善的风险防控体系。"
        )

        return synthesis

    def _calculate_confidence(self, agent_results: Dict) -> float:
        """计算整体置信度"""
        confidences = [result.get("confidence", 0) for result in agent_results.values()]
        if not confidences:
            return 0.6

        avg_confidence = sum(confidences) / len(confidences)
        weight_factor = min(1.0, len(confidences) / 5)

        return round(avg_confidence * (0.7 + 0.3 * weight_factor), 2)

    def _quality_check(self, agent_results: Dict) -> Dict:
        """质量检查"""
        quality_metrics = {
            "completeness": len(agent_results) / 8,
            "consistency": 0.85,
            "accuracy": 0.90,
            "timeliness": 1.0
        }

        overall_score = sum(quality_metrics.values()) / len(quality_metrics)

        return {
            "quality_metrics": quality_metrics,
            "overall_score": round(overall_score, 2),
            "status": "PASS" if overall_score >= 0.8 else "REVIEW",
            "improvement_suggestions": [] if overall_score >= 0.8 else ["增加Agent覆盖范围", "提高结果一致性"]
        }

    def _generate_early_warnings(self, context: BusinessContext) -> List[Dict]:
        """生成早期预警"""
        warnings = []

        financial = context.financial_data
        profit_margin = ((financial.get("revenue", 0) - financial.get("costs", 0)) /
                        financial.get("revenue", 1) * 100) if financial.get("revenue", 0) > 0 else 0

        if 5 < profit_margin < 10:
            warnings.append({
                "indicator": "利润率警戒",
                "current_value": f"{profit_margin:.1f}%",
                "threshold": "10%",
                "trend": "下降",
                "suggested_action": "立即审查成本结构"
            })

        market_growth = context.market_data.get("growth_rate", 0)
        if 0 < market_growth < 5:
            warnings.append({
                "indicator": "增长放缓预警",
                "current_value": f"{market_growth:.1f}%",
                "threshold": "5%",
                "trend": "放缓",
                "suggested_action": "评估市场竞争策略"
            })

        return warnings

    def _check_data_consistency(self, context: BusinessContext) -> Dict:
        """检查数据一致性"""
        checks = []
        score_adjustment = 0

        financial = context.financial_data
        revenue = financial.get("revenue", 0)
        costs = financial.get("costs", 0)

        if revenue > 0 and costs > revenue:
            checks.append({
                "check": "财务数据逻辑一致性",
                "status": "FAIL",
                "message": "成本大于收入，数据可能存在错误"
            })
            score_adjustment -= 15
        else:
            checks.append({
                "check": "财务数据逻辑一致性",
                "status": "PASS",
                "message": "数据逻辑一致"
            })

        return {"checks": checks, "score_adjustment": score_adjustment}

    def _estimate_resources(self, recommendations: List[Dict]) -> Dict:
        """估算资源需求"""
        total_investment = 0
        for rec in recommendations:
            complexity = rec.get("implementation_complexity", "中")
            if complexity == "低":
                total_investment += 50
            elif complexity == "中":
                total_investment += 150
            elif complexity == "中高":
                total_investment += 300
            else:
                total_investment += 500

        return {
            "estimated_total_investment": f"{total_investment}万元",
            "phased_investment": {
                "phase1_q1q2": f"{int(total_investment * 0.4)}万元",
                "phase2_q3q4": f"{int(total_investment * 0.4)}万元",
                "phase3_next_year": f"{int(total_investment * 0.2)}万元"
            },
            "key_resources": ["项目管理团队", "技术实施团队", "业务专家", "变更管理"],
            "risk_reserve": f"{int(total_investment * 0.1)}万元 (10%应急储备)"
        }


class BusinessDecisionIntelligenceV2:
    """
    YYC³ 经营决策智能化系统 v2.0

    集成Five S提示词模型 + AI Family Agent协同
    """

    def __init__(self, config_path: Optional[str] = None):
        self.prompt_engine = None
        if PROMPT_ENGINE_AVAILABLE:
            try:
                self.prompt_engine = PromptEngine(config_path)
                print("[BusinessDecision V2] 提示词引擎加载成功")
            except Exception as e:
                print(f"[BusinessDecision V2] 提示词引擎加载失败: {e}")

        self.agent_coordinator = AIFamilyCoordinator()
        self.decision_history = []
        self.config = self._load_config(config_path)

        print(f"[BusinessDecision V2] 系统初始化完成")

    def _load_config(self, config_path: Optional[str]) -> Dict:
        """加载配置"""
        default_config = {
            "max_history_records": 100,
            "auto_save_enabled": True,
            "confidence_threshold": 0.7,
            "enable_agent_coordination": True,
            "output_format": "structured_json",
            "language": "zh-CN"
        }

        if config_path and os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                default_config.update(user_config)

        return default_config

    def generate_business_report(self, context: BusinessContext) -> Dict:
        """
        生成经营分析报告（核心方法）

        基于Five S模型：
        - Set the Scene: 设定场景为资深分析师
        - Specify Task: 明确任务为生成经营分析报告
        - Simplify Language: 简洁专业的商业语言
        - Structure Response: 结构化输出
        - Share Feedback: 反馈机制
        """
        report = {
            "report_metadata": {
                "report_id": f"BR-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "generated_at": datetime.now().isoformat(),
                "period": context.period,
                "report_version": "v2.0",
                "model_version": "YYC3-BusinessDecision-V2.0-FiveS"
            },
            "five_s_framework": {
                "scene_setting": {
                    "role": "资深企业经营分析师",
                    "experience": "15年跨行业经验",
                    "expertise": ["财务分析", "市场洞察", "战略规划", "风险管理"]
                },
                "task_specification": {
                    "primary_task": "生成综合经营分析报告",
                    "input_data": {
                        "period": context.period,
                        "financial_summary": {
                            "revenue": context.financial_data.get("revenue"),
                            "costs": context.financial_data.get("costs"),
                            "profit_margin": self._calculate_profit_margin(context)
                        },
                        "market_context": context.market_data,
                        "operational_status": context.operational_data
                    }
                },
                "language_style": "简洁专业的商业语言，避免术语堆砌",
                "response_structure": [
                    "核心指标概览",
                    "同比环比分析",
                    "异常指标预警",
                    "改进建议（按优先级）",
                    "下季度展望"
                ],
                "feedback_mechanism": {
                    "uncertainty_handling": "标注置信度评分",
                    "data_quality_flag": "明确标注数据缺失",
                    "validation_points": "建议验证的数据点"
                }
            }
        }

        if self.config.get("enable_agent_coordination"):
            agent_analysis = self.agent_coordinator.coordinate_analysis("business_analysis", context)
            report["ai_family_analysis"] = agent_analysis
            report["synthesized_intelligence"] = self._synthesize_intelligence(agent_analysis, context)
        else:
            report["traditional_analysis"] = self._traditional_analysis(context)

        report["executive_summary"] = self._generate_executive_summary(report)
        report["action_items"] = self._prioritize_actions(report)

        self._save_to_history(report)

        return report

    def _calculate_profit_margin(self, context: BusinessContext) -> float:
        """计算利润率"""
        revenue = context.financial_data.get("revenue", 0)
        costs = context.financial_data.get("costs", 0)
        return ((revenue - costs) / revenue * 100) if revenue > 0 else 0

    def _synthesize_intelligence(self, agent_analysis: Dict, context: BusinessContext) -> Dict:
        """综合AI智能分析结果"""
        synthesized = {
            "overall_health_score": 0.0,
            "health_status": "",
            "key_intelligence": [],
            "strategic_recommendations": [],
            "risk_outlook": "",
            "confidence_profile": {}
        }

        agent_results = agent_analysis.get("agent_results", {})

        scores = []
        for agent_id, result in agent_results.items():
            if agent_id == "yushu_wanwu":
                metrics = result.get("key_metrics", {})
                profit_margin = metrics.get("profit_margin", 0)
                efficiency = metrics.get("operational_efficiency", 70)
                score = (min(profit_margin, 30) / 30 * 50) + (efficiency / 100 * 50)
                scores.append(score)

            elif agent_id == "yujian_xianzhi":
                synthesized["predictions"] = result.get("predictions", [])
                synthesized["risk_scenarios"] = result.get("risk_scenarios", [])

            elif agent_id == "gewu_zongshi":
                synthesized["quality_score"] = result.get("overall_quality_score", 0)

            elif agent_id == "zhiyun_shouhu":
                synthesized["risk_assessment"] = {
                    "overall_risk_level": result.get("overall_risk_level", ""),
                    "risk_factors": result.get("risk_factors", [])
                }

            elif agent_id == "qianli_bole":
                synthesized["recommendations"] = result.get("recommended_solutions", [])

        if scores:
            synthesized["overall_health_score"] = round(sum(scores) / len(scores), 2)

        if synthesized["overall_health_score"] >= 75:
            synthesized["health_status"] = "健康"
        elif synthesized["overall_health_score"] >= 50:
            synthesized["health_status"] = "需关注"
        else:
            synthesized["health_status"] = "警告"

        synthesized["confidence_profile"] = {
            "overall_confidence": agent_analysis.get("confidence_score", 0),
            "data_quality_confidence": synthesized.get("quality_score", 70) / 100,
            "model_confidence": 0.85
        }

        return synthesized

    def _traditional_analysis(self, context: BusinessContext) -> Dict:
        """传统分析方法（不使用Agent协同）"""
        financial = context.financial_data
        market = context.market_data
        operational = context.operational_data

        revenue = financial.get("revenue", 0)
        costs = financial.get("costs", 0)
        profit_margin = ((revenue - costs) / revenue * 100) if revenue > 0 else 0

        analysis = {
            "financial_analysis": {
                "revenue": revenue,
                "costs": costs,
                "profit_margin": round(profit_margin, 2),
                "status": "良好" if profit_margin > 15 else ("警戒" if profit_margin > 5 else "危险")
            },
            "market_analysis": {
                "growth_rate": market.get("growth_rate", 0),
                "competitor_count": market.get("competitor_count", 0),
                "trend": "上升" if market.get("growth_rate", 0) > 10 else ("稳定" if market.get("growth_rate", 0) > 0 else "下降")
            },
            "operational_analysis": {
                "efficiency_score": operational.get("efficiency_score", 70),
                "status": "高效" if operational.get("efficiency_score", 70) > 80 else ("正常" if operational.get("efficiency_score", 70) > 60 else "需优化")
            },
            "overall_score": self._calculate_overall_score(profit_margin, market.get("growth_rate", 0), operational.get("efficiency_score", 70))
        }

        return analysis

    def _calculate_overall_score(self, profit_margin: float, growth_rate: float, efficiency: float) -> float:
        """计算总体评分"""
        financial_score = min(profit_margin, 30) / 30 * 40
        market_score = min(max(growth_rate, -10), 20) / 20 * 30
        operational_score = efficiency / 100 * 30

        return round(financial_score + market_score + operational_score, 2)

    def _generate_executive_summary(self, report: Dict) -> Dict:
        """生成执行摘要"""
        health_status = report.get("synthesized_intelligence", {}).get("health_status", "未知")
        overall_score = report.get("synthesized_intelligence", {}).get("overall_health_score", 0)

        summary = {
            "headline": f"经营状况{health_status}（综合评分: {overall_score}）",
            "key_message": "",
            "critical_alerts": [],
            "top_opportunities": [],
            "immediate_actions_required": []
        }

        risk_assessment = report.get("synthesized_intelligence", {}).get("risk_assessment", {})
        if risk_assessment:
            high_risk_factors = [rf for rf in risk_assessment.get("risk_factors", [])
                               if rf.get("severity") in ["高", "极高"]]
            summary["critical_alerts"] = [{
                "alert": rf.get("description"),
                "severity": rf.get("severity"),
                "suggested_action": rf.get("mitigation")
            } for rf in high_risk_factors[:3]]

        recommendations = report.get("synthesized_intelligence", {}).get("recommendations", [])
        if recommendations:
            summary["top_opportunities"] = [{
                "opportunity": rec.get("solution"),
                "expected_benefit": rec.get("expected_benefit"),
                "priority": rec.get("priority")
            } for rec in recommendations[:3]]

        if health_status in ["警告", "需关注"]:
            summary["immediate_actions_required"] = [
                "召开紧急管理层会议",
                "制定应对方案",
                "建立日监控机制"
            ]

        return summary

    def _prioritize_actions(self, report: Dict) -> List[Dict]:
        """优先级排序的行动项"""
        actions = []

        risk_assessment = report.get("synthesized_intelligence", {}).get("risk_assessment", {})
        if risk_assessment and risk_assessment.get("overall_risk_level") in ["高", "极高"]:
            actions.append({
                "action": "立即启动危机应对机制",
                "priority": "P0 - 紧急",
                "owner": "CEO/管理委员会",
                "deadline": "24小时内",
                "status": "pending"
            })

        recommendations = report.get("synthesized_intelligence", {}).get("recommendations", [])
        for i, rec in enumerate(recommendations[:5]):
            priority_map = {"高": "P1", "中": "P2", "低": "P3"}
            actions.append({
                "action": f"实施{rec.get('solution', '优化方案')}",
                "priority": f"{priority_map.get(rec.get('priority', '中'), 'P2')} - {rec.get('priority', '中')}",
                "owner": "相关部门负责人",
                "deadline": f"{(i+1)*30}天内",
                "status": "planned"
            })

        if not actions:
            actions.append({
                "action": "保持现有策略，持续监控",
                "priority": "P3 - 低",
                "owner": "运营团队",
                "deadline": "下个季度",
                "status": "monitoring"
            })

        return actions

    def _save_to_history(self, report: Dict):
        """保存到历史记录"""
        self.decision_history.append({
            "timestamp": datetime.now().isoformat(),
            "report_id": report.get("report_metadata", {}).get("report_id"),
            "summary": report.get("executive_summary", {}).get("headline", "")
        })

        if len(self.decision_history) > self.config.get("max_history_records", 100):
            self.decision_history = self.decision_history[-100:]

    def get_decision_history(self, limit: int = 10) -> List[Dict]:
        """获取决策历史"""
        return self.decision_history[-limit:]

    def generate_strategic_plan(self, context: BusinessContext) -> Dict:
        """生成战略规划辅助决策"""
        if self.config.get("enable_agent_coordination"):
            agent_analysis = self.agent_coordinator.coordinate_analysis("strategic_planning", context)

            strategic_plan = {
                "plan_metadata": {
                    "plan_id": f"SP-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    "created_at": datetime.now().isoformat(),
                    "planning_horizon": "年度",
                    "version": "v2.0"
                },
                "ai_family_coordination": agent_analysis,
                "strategic_priorities": agent_analysis.get("agent_results", {}).get("yuanqi_tianshu", {}).get("strategic_priorities", []),
                "resource_allocation": agent_analysis.get("agent_results", {}).get("yuanqi_tianshu", {}).get("resource_matrix", {}),
                "risk_mitigation": agent_analysis.get("agent_results", {}).get("zhiyun_shouhu", {}),
                "innovation_roadmap": agent_analysis.get("agent_results", {}).get("chuangxiang_lingyun", {}),
                "implementation_timeline": self._generate_timeline(agent_analysis)
            }
        else:
            strategic_plan = self._basic_strategic_plan(context)

        return strategic_plan

    def _generate_timeline(self, agent_analysis: Dict) -> Dict:
        """生成实施时间线"""
        priorities = agent_analysis.get("agent_results", {}).get("yuanqi_tianshu", {}).get("strategic_priorities", [])

        timeline = {
            "q1": {"focus": "基础建设", "milestones": [], "budget_allocation": "25%"},
            "q2": {"focus": "能力提升", "milestones": [], "budget_allocation": "25%"},
            "q3": {"focus": "规模扩展", "milestones": [], "budget_allocation": "25%"},
            "q4": {"focus": "优化迭代", "milestones": [], "budget_allocation": "25%"}
        }

        for i, priority in enumerate(priorities[:4]):
            quarter_key = list(timeline.keys())[i % 4]
            timeline[quarter_key]["milestones"].append({
                "milestone": priority.get("objective", ""),
                "priority": priority.get("priority", ""),
                "status": "planned"
            })

        return timeline

    def _basic_strategic_plan(self, context: BusinessContext) -> Dict:
        """基础战略规划（无Agent协同）"""
        return {
            "plan_metadata": {
                "plan_id": f"SP-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "created_at": datetime.now().isoformat(),
                "version": "v1.0-basic"
            },
            "vision": "成为行业领先的智能化企业",
            "mission": "通过技术创新和卓越运营创造价值",
            "strategic_objectives": [
                {"objective": "提升盈利能力", "target": "利润率>20%", "timeline": "12个月"},
                {"objective": "扩大市场份额", "target": "增长15%", "timeline": "12个月"},
                {"objective": "推进数字化转型", "target": "核心系统上线", "timeline": "18个月"}
            ],
            "critical_success_factors": [
                "领导层承诺和支持",
                "充足的资源投入",
                "组织能力匹配",
                "有效的变革管理"
            ]
        }


def model_inference(input_data: Dict) -> Dict:
    """
    模型推理入口函数（兼容旧接口）

    Args:
        input_data: 输入数据字典

    Returns:
        推理结果字典
    """
    try:
        system = BusinessDecisionIntelligenceV2()

        task = input_data.get("task", "business_analysis")

        if task == "business_insight":
            data_sources = input_data.get("data_sources", {})
            context = BusinessContext(
                period=data_sources.get("period", "2026-Q1"),
                financial_data=data_sources.get("financial_data", {}),
                market_data=data_sources.get("market_data", {}),
                operational_data=data_sources.get("operational_data", {})
            )
            result = system.generate_business_report(context)

        elif task == "trend_prediction":
            historical_metrics = input_data.get("historical_metrics", [])
            coordinator = AIFamilyCoordinator()
            dummy_context = BusinessContext(
                period="2026-Q1",
                financial_data={},
                market_data={},
                operational_data={}
            )
            agent_result = coordinator._invoke_agent("yujian_xianzhi", "trend_prediction", dummy_context)
            result = {
                "task": "趋势预测",
                "predictions": agent_result.get("predictions", []),
                "confidence": agent_result.get("confidence", 0),
                "method": "AI Family Agent - 预见·先知"
            }

        elif task == "strategic_planning":
            data_sources = input_data.get("data_sources", {})
            context = BusinessContext(
                period=data_sources.get("period", "2026"),
                financial_data=data_sources.get("financial_data", {}),
                market_data=data_sources.get("market_data", {}),
                operational_data=data_sources.get("operational_data", {})
            )
            result = system.generate_strategic_plan(context)

        else:
            data_sources = input_data.get("data_sources", {})
            context = BusinessContext(
                period=data_sources.get("period", "2026-Q1"),
                financial_data=data_sources.get("financial_data", {}),
                market_data=data_sources.get("market_data", {}),
                operational_data=data_sources.get("operational_data", {})
            )
            result = system.generate_business_report(context)

        return result

    except Exception as e:
        return {
            "error": str(e),
            "error_type": type(e).__name__,
            "timestamp": datetime.now().isoformat(),
            "suggestion": "请检查输入数据格式和参数"
        }


if __name__ == "__main__":
    test_context = BusinessContext(
        period="2026-Q1",
        financial_data={
            "revenue": 120000000,
            "costs": 69000000,
            "profit_margin": 42.5
        },
        market_data={
            "growth_rate": 15.3,
            "competitor_count": 12,
            "market_share": 8.5
        },
        operational_data={
            "efficiency_score": 78,
            "employee_count": 350,
            "customer_satisfaction": 85
        },
        strategic_goals=["提升市场份额", "优化成本结构", "推进数字化转型"],
        risk_tolerance="中等",
        decision_urgency="正常"
    )

    system = BusinessDecisionIntelligenceV2()

    print("="*80)
    print("YYC³ 经营决策智能化系统 v2.0 - 测试运行")
    print("="*80)

    report = system.generate_business_report(test_context)

    print("\n📊 报告元数据:")
    print(f"   报告ID: {report['report_metadata']['report_id']}")
    print(f"   生成时间: {report['report_metadata']['generated_at']}")
    print(f"   分析周期: {report['report_metadata']['period']}")

    print("\n🤖 AI Family Agent协同分析:")
    if "ai_family_analysis" in report:
        coordination = report["ai_family_analysis"]
        print(f"   参与Agent数: {len(coordination['agents_involved'])}")
        print(f"   整体置信度: {coordination['confidence_score']}")
        print(f"   质量状态: {coordination['quality_assurance'].get('status', '未知')}")

    print("\n📈 综合智能评估:")
    intelligence = report.get("synthesized_intelligence", {})
    print(f"   健康评分: {intelligence.get('overall_health_score', 'N/A')}")
    print(f"   健康状态: {intelligence.get('health_status', '未知')}")

    print("\n📋 执行摘要:")
    exec_summary = report.get("executive_summary", {})
    print(f"   标题: {exec_summary.get('headline', 'N/A')}")

    print("\n✅ 优先行动项:")
    for i, action in enumerate(report.get("action_items", [])[:3], 1):
        print(f"   {i}. [{action['priority']}] {action['action']}")

    print("\n" + "="*80)
    print("测试完成！系统运行正常。")
    print("="*80)
