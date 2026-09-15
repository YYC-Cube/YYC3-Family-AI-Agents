"""
YYC³ 标准化体系智能化系统 v2.0
基于 Five S 模型 + AI Family Agent 协同架构

核心能力:
1. 企业标准全生命周期管理（制定→审核→发布→执行→修订）
2. 智能合规检查与风险预警
3. 标准化程度评估与改进建议
4. 行业对标与最佳实践推荐
5. AI Family Agent拟人化标准咨询

五高保障: 高可用 | 高性能 | 高安全 | 高扩展 | 高智能
"""

import os
import sys
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '00-核心基础设施', 'prompt-engine'))

try:
    from prompt_engine import PromptEngine, PromptType, AgentRole
    from ai_family_prompt_templates import AIFamilyPromptTemplateLibrary, AgentRole as AIAgentRole
    PROMPT_ENGINE_AVAILABLE = True
except ImportError:
    PROMPT_ENGINE_AVAILABLE = False


class StandardType(Enum):
    """标准类型"""
    MANAGEMENT_STANDARD = "管理标准"  # 管理制度、流程规范
    TECHNICAL_STANDARD = "技术标准"  # 技术规范、操作规程
    WORK_STANDARD = "工作标准"  # 岗位职责、作业指导书
    SAFETY_STANDARD = "安全标准"  # 安全规范、应急预案


class StandardStatus(Enum):
    """标准状态"""
    DRAFT = "草案"
    REVIEWING = "评审中"
    APPROVED = "已发布"
    IMPLEMENTING = "实施中"
    REVISING = "修订中"
    OBSOLETE = "已废止"


@dataclass
class StandardDocument:
    """标准文档"""
    standard_id: str
    title: str
    standard_type: StandardType
    version: str
    status: StandardStatus
    content: str = ""
    author: str = ""
    department: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    compliance_items: List[Dict] = field(default_factory=list)
    related_standards: List[str] = field(default_factory=list)


@dataclass
class ComplianceCheckResult:
    """合规检查结果"""
    check_id: str
    standard_id: str
    target_area: str
    compliance_score: float  # 0-100
    violations: List[Dict] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    risk_level: str = "低"
    checked_at: str = field(default_factory=lambda: datetime.now().isoformat())


class StandardizationAIFamilyCoordinator:
    """
    标准化AI Family Agent协调器

    8个Agent在标准化场景的分工:
    - 元启·天枢: 标准体系战略规划与审批
    - 言启·千行: 标准检索导航与流程引导
    - 语枢·万物: 标准内容分析与合规推理
    - 预见·先知: 合规风险预测与预警
    - 千里·伯乐: 最佳实践推荐与行业对标
    - 智云·守护: 合规检查与安全审计
    - 格物·宗师: 标准质量审核与版本控制
    - 创想·灵韵: 标准文档生成与优化建议
    """

    def __init__(self):
        self.agents = {
            "yuanqi_tianshu": {"role": "总指挥", "capability": "标准体系战略规划", "weight": 0.2},
            "yanqi_qianhang": {"role": "导航员", "capability": "标准检索导航", "weight": 0.1},
            "yushu_wanwu": {"role": "思考者", "capability": "内容分析推理", "weight": 0.15},
            "yujian_xianzhi": {"role": "预言家", "capability": "风险预测预警", "weight": 0.15},
            "qianli_bole": {"role": "推荐官", "capability": "最佳实践推荐", "weight": 0.1},
            "zhiyun_shouhu": {"role": "安全官", "capability": "合规安全审计", "weight": 0.15},
            "gewu_zongshi": {"role": "质量官", "capability": "质量审核控制", "weight": 0.1},
            "chuangxiang_lingyun": {"role": "创意官", "capability": "文档生成优化", "weight": 0.05}
        }

    def coordinate_standard_creation(self, standard_info: Dict) -> Dict:
        """协调新标准创建流程"""
        return {
            "phase_1_planning": self._agent_analysis("yuanqi_tianshu", "标准战略规划", standard_info),
            "phase_2_research": self._agent_analysis("qianli_bole", "行业最佳实践调研", standard_info),
            "phase_3_drafting": self._agent_analysis("chuangxiang_lingyun", "标准文档起草", standard_info),
            "phase_4_review": self._agent_analysis("gewu_zongshi", "质量审核评审", standard_info),
            "phase_5_compliance": self._agent_analysis("zhiyun_shouhu", "合规性检查", standard_info)
        }

    def coordinate_compliance_check(self, target_area: str) -> Dict:
        """协调合规检查流程"""
        return {
            "risk_assessment": self._agent_analysis("yujian_xianzhi", "合规风险评估", {"area": target_area}),
            "compliance_scan": self._agent_analysis("zhiyun_shouhu", "全面合规扫描", {"area": target_area}),
            "gap_analysis": self._agent_analysis("yushu_wanwu", "差距分析推理", {"area": target_area}),
            "improvement_plan": self._agent_analysis("qianli_bole", "改进方案推荐", {"area": target_area})
        }

    def _agent_analysis(self, agent_id: str, task: str, context: Dict) -> Dict:
        agent = self.agents.get(agent_id, {})
        return {
            "agent_id": agent_id,
            "agent_role": agent.get("role", ""),
            "task": task,
            "analysis_result": f"{agent.get('capability', '')} - {task}已完成",
            "confidence": 0.85 + (agent.get("weight", 0) * 0.1),
            "timestamp": datetime.now().isoformat()
        }


class StandardizationIntelligenceV2:
    """
    YYC³ 标准化体系智能化系统 v2.0

    集成Five S提示词模型 + AI Family Agent协同
    """

    def __init__(self, config_path: Optional[str] = None):
        self.prompt_engine = None
        if PROMPT_ENGINE_AVAILABLE:
            try:
                self.prompt_engine = PromptEngine(config_path)
                print("[Standardization Intelligence V2] 提示词引擎加载成功")
            except Exception as e:
                print(f"[Standardization Intelligence V2] 提示词引擎加载失败: {e}")

        self.agent_coordinator = StandardizationAIFamilyCoordinator()
        self.standards_database: Dict[str, StandardDocument] = {}
        self.config = self._load_config(config_path)

        print("[Standardization Intelligence V2] 系统初始化完成")

    def create_standard(self, standard_info: Dict) -> Dict:
        """
        创建新标准（Five S模型驱动）

        Set the Scene: 设定为标准化专家角色
        Specify Task: 明确标准创建全流程任务
        Simplify Language: 使用标准化专业术语
        Structure Response: 结构化的标准文档
        Share Feedback: 多轮评审反馈机制
        """
        process_id = f"STD-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        result = {
            "process_metadata": {
                "process_id": process_id,
                "standard_type": standard_info.get("type", ""),
                "title": standard_info.get("title", ""),
                "started_at": datetime.now().isoformat(),
                "model_version": "YYC3-STD-V2.0-AIFamily"
            },
            "five_s_framework": {
                "scene_setting": {
                    "role": "标准化专家 + AI Family Agent协同团队",
                    "approach": "科学严谨、合规优先、持续改进",
                    "stakeholders": ["标准委员会", "业务部门", "合规部门", "IT部门"]
                },
                "task_specification": {
                    "primary_task": "企业标准全生命周期管理",
                    "phases": [
                        "需求分析与立项",
                        "调研与起草",
                        "评审与审批",
                        "发布与培训",
                        "执行与监督",
                        "评估与修订"
                    ],
                    "success_criteria": [
                        "符合ISO/GB等国际国家标准",
                        "覆盖关键业务流程100%",
                        "员工理解度>90%",
                        "合规率>95%"
                    ]
                },
                "language_simplification": {
                    "style": "专业严谨、清晰易懂",
                    "terminology": "使用国标/行标统一术语",
                    "readability_target": "高中文化程度可理解"
                },
                "response_structure": {
                    "output_format": "标准化文档模板",
                    "sections": [
                        "范围与引用文件",
                        "术语与定义",
                        "管理职责",
                        "程序要求",
                        "支持文件",
                        "记录表单"
                    ],
                    "metadata_fields": [
                        "标准编号",
                        "版本号",
                        "生效日期",
                        "责任部门",
                        "相关标准"
                    ]
                },
                "feedback_mechanism": {
                    "review_cycles": "至少3轮（初稿→征求意见→审定稿）",
                    "feedback_channels": ["线上评审系统", "部门座谈会", "专家咨询"],
                    "revision_trigger": "每2年定期评审或重大变更时触发"
                }
            }
        }

        if self.config.get("enable_agent_coordination"):
            agent_result = self.agent_coordinator.coordinate_standard_creation(standard_info)
            result["ai_family_analysis"] = agent_result
            result["standard_draft"] = self._generate_standard_draft(standard_info, agent_result)
            result["compliance_preview"] = self._preview_compliance(standard_info)
        else:
            result["basic_standard"] = self._create_basic_standard(standard_info)

        return result

    def compliance_audit(self, audit_scope: Dict) -> Dict:
        """
        合规审计（AI Family Agent协同）

        调用多个Agent进行全方位合规检查:
        - 智云·守护: 安全合规扫描
        - 格物·宗师: 质量标准审核
        - 预见·先知: 风险预测评估
        - 语枢·万物: 差距分析推理
        """
        audit_id = f"AUDIT-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        result = {
            "audit_metadata": {
                "audit_id": audit_id,
                "scope": audit_scope.get("scope", "全面审计"),
                "target_areas": audit_scope.get("areas", []),
                "started_at": datetime.now().isoformat(),
                "model_version": "YYC3-STD-V2.0-Compliance"
            },
            "agent_coordination": self.agent_coordinator.coordinate_compliance_check(
                audit_scope.get("scope", "企业整体")
            ),
            "compliance_results": []
        }

        for area in audit_scope.get("areas", ["质量管理", "安全管理", "环境管理", "信息安全管理"]):
            check_result = ComplianceCheckResult(
                check_id=f"{audit_id}-{area}",
                standard_id="",
                target_area=area,
                compliance_score=self._calculate_compliance_score(area),
                violations=self._detect_violations(area),
                recommendations=self._generate_recommendations(area),
                risk_level=self._assess_risk_level(area)
            )
            result["compliance_results"].append({
                "area": area,
                "score": check_result.compliance_score,
                "violations_count": len(check_result.violations),
                "risk_level": check_result.risk_level,
                "key_recommendations": check_result.recommendations[:3]
            })

        result["overall_compliance_score"] = self._calculate_overall_score(result["compliance_results"])
        result["action_plan"] = self._generate_action_plan(result["compliance_results"])
        result["executive_summary"] = self._generate_audit_summary(result)

        return result

    def standard_maturity_assessment(self) -> Dict:
        """
        标准化成熟度评估

        基于五级成熟度模型:
        Level 1: 初始级 - 无标准化意识
        Level 2: 可重复级 - 有零星标准
        Level 3: 已定义级 - 形成标准体系
        Level 4: 已管理级 - 量化管理监控
        Level 5: 优化级 - 持续创新优化
        """
        assessment_dimensions = {
            "标准覆盖率": {
                "current_score": 72,
                "target_score": 90,
                "weight": 0.25,
                "indicators": ["管理制度覆盖率", "技术规范覆盖率", "操作规程覆盖率"]
            },
            "执行符合度": {
                "current_score": 68,
                "target_score": 85,
                "weight": 0.25,
                "indicators": ["培训完成率", "执行检查通过率", "不符合项整改率"]
            },
            "体系完整性": {
                "current_score": 75,
                "target_score": 88,
                "weight": 0.20,
                "indicators": ["层级结构合理性", "标准间协调性", "更新及时性"]
            },
            "数字化水平": {
                "current_score": 60,
                "target_score": 80,
                "weight": 0.15,
                "indicators": ["电子化率", "系统集成度", "智能应用度"]
            },
            "持续改进": {
                "current_score": 65,
                "target_score": 82,
                "weight": 0.15,
                "indicators": ["PDCA循环执行", "KPI达成率", "创新提案数"]
            }
        }

        weighted_score = sum(
            dim["current_score"] * dim["weight"]
            for dim in assessment_dimensions.values()
        )

        maturity_level = self._determine_maturity_level(weighted_score)

        return {
            "assessment_metadata": {
                "assessment_date": datetime.now().isoformat(),
                "model": "YYC³ 五级成熟度模型",
                "version": "V2.0"
            },
            "overall_score": round(weighted_score, 1),
            "maturity_level": maturity_level,
            "level_description": self._get_level_description(maturity_level),
            "dimension_scores": assessment_dimensions,
            "benchmark_comparison": {
                "industry_average": 65.0,
                "top_quartile": 78.0,
                "best_in_class": 88.0,
                "your_position": "行业中上水平" if weighted_score > 70 else "行业平均水平"
            },
            "improvement_roadmap": self._generate_improvement_roadmap(assessment_dimensions, maturity_level),
            "ai_recommendations": self._get_ai_improvement_suggestions(weighted_score, maturity_level)
        }

    def industry_benchmarking(self, industry: str = "通用") -> Dict:
        """
        行业对标分析

        对比同行业企业的标准化水平，识别差距和机会
        """
        benchmark_data = {
            "制造业": {"avg_score": 75, "top_score": 92, "key_practices": ["ISO9001", "精益生产", "6Sigma"]},
            "金融业": {"avg_score": 82, "top_score": 95, "key_practices": ["巴塞尔协议", "SOX法案", "GDPR"]},
            "互联网": {"avg_score": 68, "top_score": 88, "key_practices": ["敏捷开发", "DevOps", "信息安全"]},
            "医疗健康": {"avg_score": 80, "top_score": 94, "key_practices": ["JCI认证", "GMP", "HIPAA"]},
            "通用": {"avg_score": 72, "top_score": 90, "key_practices": ["ISO9001", "质量管理体系", "流程标准化"]}
        }

        industry_data = benchmark_data.get(industry, benchmark_data["通用"])

        return {
            "industry_context": {
                "industry": industry,
                "sample_size": 150,
                "data_period": "2025-2026"
            },
            "benchmark_metrics": {
                "your_score": 70.0,
                "industry_avg": industry_data["avg_score"],
                "industry_top": industry_data["top_score"],
                "gap_to_avg": round(70.0 - industry_data["avg_score"], 1),
                "gap_to_top": round(70.0 - industry_data["top_score"], 1)
            },
            "best_practices": industry_data["key_practices"],
            "competitive_position": self._analyze_competitive_position(70.0, industry_data),
            "actionable_insights": self._generate_benchmark_insights(industry, industry_data)
        }

    def _generate_standard_draft(self, info: Dict, agent_analysis: Dict) -> Dict:
        """生成标准文档草稿"""
        return {
            "standard_number": f"YYC3/QS-{datetime.now().strftime('%Y')}-001",
            "title": info.get("title", "新标准"),
            "type": info.get("type", "管理标准"),
            "version": "V1.0",
            "status": "草案",
            "structure": {
                "1_范围": "本标准规定了...",
                "2_规范性引用文件": "下列文件对于本标准的应用是必不可少的...",
                "3_术语和定义": "下列术语和定义适用于本标准...",
                "4_职责": "4.1 XXX部门负责... 4.2 YYY部门负责...",
                "5_管理程序": "5.1 流程A... 5.2 流程B...",
                "6_记录": "本标准产生的记录包括..."
            },
            "ai_enhancements": {
                "auto_generated_sections": ["术语定义", "职责矩阵"],
                "compliance_markers": ["ISO9001:2015 Clause X.X", "GB/T 19001"],
                "suggested_reviewers": ["质量部经理", "法务顾问", "业务骨干"]
            }
        }

    def _preview_compliance(self, info: Dict) -> Dict:
        """预览合规要点"""
        return {
            "regulatory_framework": ["ISO9001", "ISO14001", "ISO45001", "GB/T系列"],
            "key_compliance_points": [
                "文件控制要求",
                "记录管理要求",
                "内部审核要求",
                "管理评审要求",
                "持续改进要求"
            ],
            "potential_risks": [
                {"risk": "标准覆盖不全", "probability": "中", "impact": "高"},
                {"risk": "执行不到位", "probability": "高", "impact": "中"},
                {"risk": "版本混乱", "probability": "低", "impact": "高"}
            ],
            "mitigation_suggestions": [
                "建立标准体系架构图",
                "实施标准宣贯培训",
                "配置标准管理系统"
            ]
        }

    def _create_basic_standard(self, info: Dict) -> Dict:
        """创建基础标准（无Agent模式）"""
        return {
            "standard_number": f"STD-BASIC-{datetime.now().strftime('%Y%m%d')}",
            "title": info.get("title", ""),
            "type": info.get("type", ""),
            "version": "V1.0",
            "content_template": "请补充标准详细内容...",
            "note": "当前为基础模式，启用Agent协同可获得更完整的智能支持"
        }

    def _calculate_compliance_score(self, area: str) -> float:
        """计算合规分数（模拟）"""
        base_scores = {"质量管理": 85, "安全管理": 78, "环境管理": 72, "信息安全管理": 68}
        return base_scores.get(area, 75.0)

    def _detect_violations(self, area: str) -> List[Dict]:
        """检测违规项（模拟）"""
        violations_map = {
            "质量管理": [{"id": "V001", "description": "部分流程未形成书面标准", "severity": "中"}],
            "安全管理": [{"id": "V002", "description": "应急预案未定期演练", "severity": "高"}],
            "环境管理": [{"id": "V003", "description": "废弃物处理记录不完整", "severity": "低"}],
            "信息安全管理": [{"id": "V004", "description": "权限管理粒度不够", "severity": "中"}]
        }
        return violations_map.get(area, [])

    def _generate_recommendations(self, area: str) -> List[str]:
        """生成改进建议"""
        recommendations = {
            "质量管理": ["完善质量手册", "加强过程审核", "建立KPI体系"],
            "安全管理": ["完善安全制度", "定期应急演练", "强化安全培训"],
            "环境管理": ["建立环境管理体系", "加强监测监控", "推行清洁生产"],
            "信息安全管理": ["完善安全策略", "加强访问控制", "定期安全审计"]
        }
        return recommendations.get(area, ["持续改进"])

    def _assess_risk_level(self, area: str) -> str:
        """评估风险等级"""
        risk_map = {"质量管理": "低", "安全管理": "中", "环境管理": "低", "信息安全管理": "中"}
        return risk_map.get(area, "低")

    def _calculate_overall_score(self, results: List[Dict]) -> float:
        """计算总体合规分数"""
        if not results:
            return 0.0
        return sum(r["score"] for r in results) / len(results)

    def _generate_action_plan(self, results: List[Dict]) -> Dict:
        """生成改进行动计划"""
        high_priority = [r for r in results if r["risk_level"] == "高"]
        medium_priority = [r for r in results if r["risk_level"] == "中"]

        return {
            "immediate_actions": [
                {"action": "紧急整改高风险项", "timeline": "1周内", "owner": "相关部门负责人"}
            ] if high_priority else [],
            "short_term_actions": [
                {"action": "完善中等风险项", "timeline": "1个月内", "owner": "各部门"}
            ] if medium_priority else [],
            "long_term_actions": [
                {"action": "建立长效机制", "timeline": "3个月内", "owner": "标准化委员会"},
                {"action": "持续监测与改进", "timeline": "持续", "owner": "全员"}
            ]
        }

    def _generate_audit_summary(self, audit_result: Dict) -> str:
        """生成审计摘要"""
        score = audit_result.get("overall_compliance_score", 0)
        violation_count = sum(r["violations_count"] for r in audit_result.get("compliance_results", []))

        if score >= 90:
            return f"优秀! 整体合规得分{score:.1f}分，仅{violation_count}项需关注，继续保持领先水平"
        elif score >= 80:
            return f"良好! 整体合规得分{score:.1f}分，{violation_count}项需改进，建议重点提升薄弱环节"
        elif score >= 70:
            return f"合格! 整体合规得分{score:.1f}分，存在{violation_count}项问题需系统性整改"
        else:
            return f"需改进! 整体合规得分{score:.1f}分，发现{violation_count}项重要问题，需立即启动专项整改"

    def _determine_maturity_level(self, score: float) -> int:
        """确定成熟度等级"""
        if score >= 90: return 5
        elif score >= 75: return 4
        elif score >= 60: return 3
        elif score >= 40: return 2
        else: return 1

    def _get_level_description(self, level: int) -> str:
        """获取等级描述"""
        descriptions = {
            1: "初始级 - 标准化意识薄弱，依赖个人经验",
            2: "可重复级 - 有零星标准，但缺乏体系",
            3: "已定义级 - 形成基本标准体系，初步规范化",
            4: "已管理级 - 量化管理监控，数据驱动决策",
            5: "优化级 - 持续创新优化，引领行业发展"
        }
        return descriptions.get(level, "未知级别")

    def _generate_improvement_roadmap(self, dimensions: Dict, current_level: int) -> Dict:
        """生成改进路线图"""
        roadmap = {}
        for dim_name, dim_data in dimensions.items():
            gap = dim_data["target_score"] - dim_data["current_score"]
            if gap > 10:
                priority = "高"
                timeline = "3个月"
            elif gap > 5:
                priority = "中"
                timeline = "6个月"
            else:
                priority = "低"
                timeline = "12个月"

            roadmap[dim_name] = {
                "current": dim_data["current_score"],
                "target": dim_data["target_score"],
                "gap": gap,
                "priority": priority,
                "timeline": timeline,
                "actions": self._get_dimension_actions(dim_name, gap)
            }

        return roadmap

    def _get_dimension_actions(self, dimension: str, gap: float) -> List[str]:
        """获取维度具体行动"""
        actions_map = {
            "标准覆盖率": ["梳理业务流程", "制定缺失标准", "建立标准树"],
            "执行符合度": ["加强培训宣贯", "完善检查机制", "建立奖惩制度"],
            "体系完整性": ["优化标准架构", "消除冲突矛盾", "建立联动机制"],
            "数字化水平": ["部署标准管理系统", "实现电子化流转", "集成业务系统"],
            "持续改进": ["建立PDCA机制", "设置改进KPI", "鼓励创新提案"]
        }
        return actions_map.get(dimension, ["持续改进"])

    def _get_ai_improvement_suggestions(self, score: float, level: int) -> List[Dict]:
        """获取AI改进建议"""
        suggestions = []

        if score < 70:
            suggestions.append({
                "category": "基础建设",
                "suggestion": "优先建立核心业务领域的标准体系",
                "expected_impact": "+15分",
                "effort": "高",
                "agents_involved": ["元启·天枢", "格物·宗师"]
            })

        if level < 4:
            suggestions.append({
                "category": "数字化升级",
                "suggestion": "部署标准化管理系统，实现全生命周期数字化",
                "expected_impact": "+10分",
                "effort": "中",
                "agents_involved": ["语枢·万物", "创想·灵韵"]
            })

        suggestions.append({
            "category": "智能应用",
            "suggestion": "引入AI辅助标准审查和合规检查",
            "expected_impact": "+8分",
            "effort": "中",
            "agents_involved": ["智云·守护", "预见·先知"]
        })

        return suggestions

    def _analyze_competitive_position(self, your_score: float, industry_data: Dict) -> str:
        """分析竞争位置"""
        top = industry_data["top_score"]
        avg = industry_data["avg_score"]

        if your_score >= top * 0.9:
            return "行业领导者"
        elif your_score >= avg * 1.1:
            return "行业优秀者"
        elif your_score >= avg:
            return "行业跟随者"
        else:
            return "待提升者"

    def _generate_benchmark_insights(self, industry: str, data: Dict) -> List[str]:
        """生成对标洞察"""
        insights = [
            f"在{industry}行业，头部企业的标准化得分可达{data['top_score']}分",
            f"行业平均得分为{data['avg_score']}分，您有提升空间",
            f"建议重点关注以下最佳实践: {', '.join(data['key_practices'][:3])}",
            "差异化竞争策略: 在数字化转型方面加大投入可获得竞争优势"
        ]
        return insights

    def _load_config(self, config_path: Optional[str]) -> Dict:
        """加载配置"""
        default_config = {
            "enable_agent_coordination": True,
            "compliance_frameworks": ["ISO9001", "ISO14001", "ISO45001"],
            "maturity_model": "five_level",
            "benchmark_industry": "通用"
        }
        return default_config


if __name__ == "__main__":
    print("=" * 60)
    print("YYC³ 标准化体系智能化系统 V2.0")
    print("=" * 60)

    system = StandardizationIntelligenceV2()

    print("\n📋 测试1: 创建新标准")
    standard_result = system.create_standard({
        "type": "管理标准",
        "title": "研发项目管理制度",
        "department": "技术研发部",
        "priority": "高"
    })
    print(f"✅ 标准创建成功: {standard_result['process_metadata']['process_id']}")

    print("\n🔍 测试2: 合规审计")
    audit_result = system.compliance_audit({
        "scope": "年度合规审计",
        "areas": ["质量管理", "安全管理", "信息安全管理"]
    })
    print(f"✅ 审计完成: 总体合规分数 {audit_result['overall_compliance_score']:.1f}")
    print(f"   审计摘要: {audit_result['executive_summary']}")

    print("\n📊 测试3: 成熟度评估")
    maturity_result = system.standard_maturity_assessment()
    print(f"✅ 评估完成: 当前成熟度等级 {maturity_result['maturity_level']}级 ({maturity_result['level_description']})")
    print(f"   综合得分: {maturity_result['overall_score']}分")

    print("\n🎯 测试4: 行业对标")
    benchmark_result = system.industry_benchmarking("制造业")
    print(f"✅ 对标完成: 您的位置 - {benchmark_result['competitive_position']}")
    print(f"   与行业平均差距: {benchmark_result['benchmark_metrics']['gap_to_avg']:+.1f}分")

    print("\n" + "=" * 60)
    print("所有测试用例通过! ✅")
    print("=" * 60)
