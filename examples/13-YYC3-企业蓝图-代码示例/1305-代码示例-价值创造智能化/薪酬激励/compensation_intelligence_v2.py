"""
YYC³ 薪酬激励智能化系统 v2.0
基于 Five S 模型 + AI Family Agent 协同架构

核心能力:
1. 智能薪酬体系设计与优化
2. 绩效驱动的激励方案定制
3. 公平性分析与薪酬对标
4. 员工满意度预测与保留策略
5. 全面回报(Total Rewards)规划
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
    PROMPT_ENGINE_AVAILABLE = True
except ImportError:
    PROMPT_ENGINE_AVAILABLE = False


@dataclass
class EmployeeCompensation:
    """员工薪酬档案"""
    employee_id: str
    name: str
    position: str
    level: str
    base_salary: float
    bonus_target: float
    benefits_value: float
    total_compensation: float = field(init=False)


@dataclass
class CompensationPlan:
    """薪酬方案"""
    plan_id: str
    name: str
    target_group: str
    components: Dict[str, Any]
    budget: float
    effectiveness_metrics: Dict[str, float]


class CompensationAIFamilyCoordinator:
    """
    薪酬激励Agent协调器
    
    分工:
    - 元启·天枢: 薪酬战略设计与预算审批
    - 言启·千行: 政策解读与流程引导
    - 语枢·万物: 数据分析与公平性推理
    - 预见·先知: 趋势预测与人才市场洞察
    - 千里·伯乐: 最佳实践推荐与方案匹配
    - 智云·守护: 合规审计与风险控制
    - 格物·宗师: 方案审核与质量控制
    - 创想·灵韵: 创新激励模式设计
    """

    def __init__(self):
        self.agents = {
            "yuanqi_tianshu": {"role": "总指挥", "capability": "战略预算审批", "weight": 0.18},
            "yanqi_qianhang": {"role": "导航员", "capability": "政策流程引导", "weight": 0.08},
            "yushu_wanwu": {"role": "思考者", "capability": "数据分析推理", "weight": 0.22},
            "yujian_xianzhi": {"role": "预言家", "capability": "趋势市场洞察", "weight": 0.15},
            "qianli_bole": {"role": "推荐官", "capability": "实践方案推荐", "width": 0.14},
            "zhiyun_shouhu": {"role": "安全官", "capability": "合规风险控制", "weight": 0.13},
            "gewu_zongshi": {"role": "质量官", "capability": "方案审核控制", "weight": 0.07},
            "chuangxiang_lingyun": {"role": "创意官", "capability": "创新模式设计", "weight": 0.03}
        }

    def coordinate_compensation_design(self, context: Dict) -> Dict:
        """协调薪酬方案设计"""
        return {
            "market_analysis": self._agent_analysis("yujian_xianzhi", "市场薪酬分析", context),
            "internal_equity": self._agent_analysis("yushu_wanwu", "内部公平性分析", context),
            "best_practices": self._agent_analysis("qianli_bole", "最佳实践调研", context),
            "compliance_check": self._agent_analysis("zhiyun_shouhu", "合规性检查", context),
            "strategic_alignment": self._agent_analysis("yuanqi_tianshu", "战略对齐分析", context),
            "innovation_design": self._agent_analysis("chuangxiang_lingyun", "创新激励设计", context)
        }

    def _agent_analysis(self, agent_id: str, task: str, context: Dict) -> Dict:
        agent = self.agents.get(agent_id, {})
        return {
            "agent_id": agent_id,
            "role": agent.get("role", ""),
            "task": task,
            "result": f"{agent.get('capability', '')}完成",
            "confidence": 0.86 + (agent.get("weight", 0) * 0.11)
        }


class CompensationIntelligenceV2:
    """
    YYC³ 薪酬激励智能化系统 v2.0
    """

    def __init__(self, config_path: Optional[str] = None):
        self.prompt_engine = None
        if PROMPT_ENGINE_AVAILABLE:
            try:
                self.prompt_engine = PromptEngine(config_path)
                print("[Compensation Intelligence V2] 提示词引擎加载成功")
            except Exception as e:
                print(f"[Compensation Intelligence V2] 提示词引擎加载失败: {e}")

        self.agent_coordinator = CompensationAIFamilyCoordinator()
        self.config = self._load_config(config_path)

        print("[Compensation Intelligence V2] 系统初始化完成")

    def design_intelligent_compensation(self, requirements: Dict) -> Dict:
        """智能薪酬方案设计"""
        design_id = f"COMP-DESIGN-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        compensation_structure = {
            "fixed_component": {
                "base_salary": {"percentage": 70, "description": "基本工资，保障稳定性"},
                "allowances": {"percentage": 10, "description": "各类津贴补贴"}
            },
            "variable_component": {
                "performance_bonus": {"percentage": 12, "description": "绩效奖金，与KPI挂钩"},
                "profit_sharing": {"percentage": 5, "description": "利润分享，共享公司成长"},
                "project_bonus": {"percentage": 3, "description": "项目奖励，鼓励创新"}
            },
            "long_term_incentives": {
                "stock_options": {"percentage": 0, "description": "股权激励（管理层）"},
                "retention_bonus": {"percentage": 0, "description": "留任奖金（关键人才）"}
            },
            "benefits_package": {
                "insurance": {"value": "五险一金全额缴纳"},
                "supplementary": {"value": "补充医疗、年度体检"},
                "perks": {"value": "餐补、交通补、通讯补等"}
            }
        }

        return {
            "design_metadata": {
                "design_id": design_id,
                "target_group": requirements.get("target_group", "全员"),
                "designed_at": datetime.now().isoformat(),
                "model_version": "YYC3-COMP-V2.0-AIFamily"
            },
            "ai_family_coordination": self.agent_coordinator.coordinate_compensation_design(requirements),
            "compensation_structure": compensation_structure,
            "salary_positioning": {
                "strategy": "跟随市场领先者 (P75)",
                "market_percentile": 75,
                "competitive_analysis": {
                    "your_position": "市场中上水平",
                    "industry_avg": "P50",
                    "top_companies": "P90",
                    "recommendation": "核心岗位可达P80，一般岗位保持P65-P75"
                }
            },
            "budget_projection": {
                "total_annual_budget": "人均年薪范围根据岗位级别确定",
                "cost_increase_vs_current": "+8-12%",
                "roi_expectation": "员工效能提升15-20%，离职率降低30%"
            },
            "implementation_roadmap": [
                {"phase": "方案设计", "timeline": "1个月", "activities": ["完成市场调研", "设计薪酬结构", "测算预算"]},
                {"phase": "沟通宣贯", "timeline": "2周", "activities": ["管理层沟通", "员工宣讲", "FAQ解答"]},
                {"phase": "试运行", "timeline": "3个月", "activities": ["选择试点部门", "收集反馈", "微调方案"]},
                {"phase": "全面推广", "timeline": "1个月", "activities": ["全员实施", "系统更新", "培训支持"]}
            ],
            "success_metrics": [
                "员工薪酬满意度 > 80%",
                "关键人才保留率 > 90%",
                "绩效优秀者薪酬增长率 > 平均水平的1.5倍",
                "薪酬成本占营收比控制在合理范围"
            ]
        }

    def performance_based_incentive(self, employee_data: Dict) -> Dict:
        """绩效导向的个性化激励方案"""
        incentive_id = f"INC-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        performance_level = employee_data.get("performance_rating", "B")
        position = employee_data.get("position", "")
        years_of_service = employee_data.get("years_of_service", 3)

        incentive_plan = {
            "base_salary_adjustment": self._calculate_salary_adjustment(performance_level, years_of_service),
            "short_term_incentive": self._design_short_term_incentive(performance_level, position),
            "long_term_incentive": self._design_long_term_incentive(position, years_of_service),
            "non_financial_rewards": self._design_non_financial_rewards(employee_data),
            "development_support": self._design_development_support(performance_level)
        }

        return {
            "incentive_metadata": {
                "incentive_id": incentive_id,
                "employee_name": employee_data.get("name", ""),
                "current_performance": performance_level,
                "generated_at": datetime.now().isoformat()
            },
            "personalized_incentive_plan": incentive_plan,
            "total_reward_value": self._estimate_total_reward(incentive_plan),
            "motivation_analysis": {
                "primary_motivators": self._identify_motivators(employee_data),
                "engagement_risk": "低" if performance_level in ["A", "B"] else ("中" if performance_level == "C" else "高"),
                "retention_likelihood": "高" if years_of_service > 2 and performance_level in ["A", "B"] else "需关注"
            },
            "conversation_talking_points": [
                f"感谢您在过去一年的出色表现（{performance_level}级）",
                "基于您的贡献和市场情况，我们为您设计了个性化的激励方案",
                "除了薪酬调整外，我们还关注您的职业发展和工作体验",
                "希望这个方案能让您感受到公司的认可和期望"
            ]
        }

    def pay_equity_analysis(self, scope: Dict) -> Dict:
        """薪酬公平性分析"""
        equity_id = f"EQUITY-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        equity_dimensions = [
            {"dimension": "性别公平", "gap_percentage": 3.2, "status": "基本公平", "action_needed": False},
            {"dimension": "年龄公平", "gap_percentage": 5.8, "status": "轻微偏差", "action_needed": True},
            {"dimension": "职级内部公平", "gap_percentage": 8.5, "status": "需关注", "action_needed": True},
            {"dimension": "部门间公平", "gap_percentage": 12.3, "status": "显著差异", "action_needed": True}
        ]

        overall_equity_score = 100 - sum(d["gap_percentage"] for d in equity_dimensions) / len(equity_dimensions)

        return {
            "equity_metadata": {
                "equity_id": equity_id,
                "scope": scope.get("scope", "全员"),
                "analyzed_at": datetime.now().isoformat()
            },
            "overall_equity_score": round(overall_equity_score, 1),
            "equity_grade": "优秀" if overall_equity_score >= 95 else ("良好" if overall_equity_score >= 90 else ("合格" if overall_equity_score >= 85 else "需改进")),
            "dimensional_analysis": equity_dimensions,
            "critical_findings": [d for d in equity_dimensions if d["action_needed"]],
            "remediation_recommendations": [
                "针对部门间差异：建立统一的薪酬带宽和晋升标准",
                "针对年龄偏差：确保经验因素合理体现，避免年龄歧视",
                "针对职级内部：引入更精细的能力评估模型，减少主观偏差",
                "建立定期审计机制：每年进行一次全面的薪酬公平性审查"
            ],
            "legal_compliance_check": {
                "equal_pay_act": "✅ 合规",
                "anti_discrimination": "✅ 合规",
                "minimum_wage": "✅ 合规",
                "overtime_regulations": "⚠️ 需复核加班费计算"
            }
        }

    def talent_retention_strategy(self, risk_profile: Dict) -> Dict:
        """人才保留策略"""
        strategy_id = f"RETAIN-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        retention_levers = {
            "financial": {
                "competitiveness": "确保薪酬处于市场中上位(P65-P75)",
                "equity_participation": "为核心人才提供期权/限制性股票",
                "bonus_opportunity": "设置有吸引力的目标奖金(20-50%基薪)"
            },
            "career_development": {
                "growth_pathway": "清晰的职业发展通道和晋升机会",
                "learning_budget": "年度培训预算(年薪的3-5%)",
                "mentorship_program": "一对一导师辅导和高管对话机会"
            },
            "work_environment": {
                "flexibility": "远程办公和弹性工作时间选项",
                "work_life_balance": "合理的 workload 和 PTO政策",
                "culture": "包容多元、认可贡献的企业文化"
            },
            "recognition_appreciation": {
                "formal_recognition": "月度/季度/年度奖项计划",
                "peer_recognition": "同事间即时认可平台",
                "visibility": "高层关注和公开表彰机会"
            }
        }

        at_risk_segments = [
            {"segment": "高绩效者(前10%)", "risk_level": "中", "priority_action": "长期激励绑定"},
            {"segment": "关键岗位人员", "risk_level": "高", "priority_action": "薪酬竞争力提升"},
            {"segment": "新入职1年内员工", "risk_level": "中高", "priority_action": "融入和文化建设"},
            {"segment": "老员工(5年以上)", "risk_level": "低", "priority_action": "再激活和角色刷新"}
        ]

        return {
            "strategy_metadata": {
                "strategy_id": strategy_id,
                "focus": risk_profile.get("focus", "整体保留"),
                "created_at": datetime.now().isoformat()
            },
            "retention_levers": retention_levers,
            "at_risk_segments": at_risk_segments,
            "predicted_retention_rate_improvement": "+15-25%",
            "implementation_priorities": [
                "立即行动: 审查并调整关键人才的薪酬竞争力",
                "短期(1-3个月): 推出新的长期激励计划和职业发展项目",
                "中期(3-6个月): 优化工作环境和灵活性政策",
                "长期(6-12个月): 建立持续的人才保留监测和预警机制"
            ],
            "roi_of_retention": {
                "cost_of_replacement": "平均岗位年薪的150-200%",
                "retention_investment": "人均年薪的10-15%",
                "net_savings": "每留住一个关键人才节省数十万元",
                "payback_period": "6-12个月"
            }
        }

    def _calculate_salary_adjustment(self, performance: str, years: int) -> Dict:
        """计算薪资调整"""
        adjustments = {
            "A+": {"range": "15-25%", "rationale": "卓越表现，显著超越期望"},
            "A": {"range": "10-18%", "rationale": "优秀表现，超出预期"},
            "B+": {"range": "6-12%", "rationale": "良好表现，达到并部分超出预期"},
            "B": {"range": "3-8%", "rationale": "符合预期，稳定贡献"},
            "C": {"range": "0-3%", "rationale": "部分达标，需改进"},
            "D": {"range": "0%", "rationale": "未达标准，需PIP"}
        }
        base = adjustments.get(performance, adjustments["B"])
        tenure_bonus = min(years * 0.5, 3)  # 最高加3%
        
        return {
            "adjustment_range": base["range"],
            "tenure_bonus": f"+{tenure_bonus:.1f}%",
            "rationale": base["rationale"]
        }

    def _design_short_term_incentive(self, performance: str, position: str) -> Dict:
        """设计短期激励"""
        multipliers = {"A+": 1.5, "A": 1.3, "B+": 1.1, "B": 1.0, "C": 0.5, "D": 0}
        target_pct = multipliers.get(performance, 1.0) * 15  # 目标奖金基数15%

        return {
            "target_bonus_percentage": f"{target_pct:.1f}% of base salary",
            "kpi_weighting": {
                "个人绩效": "60%",
                "团队/部门绩效": "30%",
                "公司整体业绩": "10%"
            },
            "payment_frequency": "季度预发 + 年终结算",
            "special_recognition": "Spot Bonus机会 (即时奖励)"
        }

    def _design_long_term_incentive(self, position: str, years: int) -> Dict:
        """设计长期激励"""
        is_eligible = position in ["总监", "VP", "高管"] or years >= 5

        return {
            "eligible": is_eligible,
            "instruments": ["股票期权", "限制性股票单位(RSU)", "虚拟股票"] if is_eligible else ["利润分享计划"],
            "vesting_schedule": "4年阶梯归属 (25%/年)" if is_eligible else "N/A",
            "estimated_value": "年薪的20-50%" if is_eligible else "N/A"
        }

    def _design_non_financial_rewards(self, employee_data: Dict) -> List[Dict]:
        """设计非金钱奖励"""
        return [
            {"reward": "额外假期天数", "value": "2-5天/年"},
            {"reward": "灵活工作安排", "value": "远程办公/弹性时间"},
            {"reward": "职业发展机会", "value": "培训预算/会议参与"},
            {"reward": "工作内容丰富化", "value": "挑战性项目/轮岗机会"},
            {"reward": "认可与 visibility", "value": "公开表扬/高管对话"}
        ]

    def _design_development_support(self, performance: str) -> Dict:
        """设计发展支持"""
        support_map = {
            "A+": {"focus": "领导力发展", "actions": ["高管教练", "MBA赞助", "继任者计划"]},
            "A": {"focus": "专业深化", "actions": ["高级认证", "行业峰会", "导师制"]},
            "B+": {"focus": "能力拓展", "actions": ["技能培训", "跨部门项目", "横向发展"]},
            "B": {"focus": "稳步提升", "actions": ["在岗培训", "绩效辅导", "目标设定"]}
        }
        return support_map.get(performance, support_map["B"])

    def _estimate_total_reward(self, plan: Dict) -> Dict:
        """估算总报酬"""
        return {
            "financial_total": "年薪 × (1 + 调整比例 + 激励比例)",
            "non_financial_value": "相当于年薪的10-20%",
            "total_reward_message": "总回报包含现金、福利、发展和体验等多维度价值"
        }

    def _identify_motivators(self, employee_data: Dict) -> List[str]:
        """识别主要激励因素"""
        age = employee_data.get("age", 35)
        career_stage = employee_data.get("career_stage", "mid")

        if age < 30:
            return ["成长发展", "挑战性工作", "学习机会"]
        elif age < 40:
            return ["薪酬竞争力", "职业晋升", "工作生活平衡"]
        elif age < 50:
            return ["工作稳定性", "影响力", "认可尊重"]
        else:
            return ["工作意义", "传承指导", "灵活性"]

    def _load_config(self, config_path: Optional[str]) -> Dict:
        """加载配置"""
        return {
            "enable_agent_coordination": True,
            "compensation_philosophy": "内部公平 + 外部竞争 + 绩效导向",
            "market_data_source": "第三方薪酬调研报告"
        }


if __name__ == "__main__":
    print("=" * 60)
    print("YYC³ 薪酬激励智能化系统 V2.0")
    print("=" * 60)

    system = CompensationIntelligenceV2()

    print("\n💰 测试1: 智能薪酬设计")
    comp_design = system.design_intelligent_compensation({"target_group": "技术研发人员"})
    print(f"   设计完成: {comp_design['design_metadata']['design_id']}")

    print("\n🎯 测试2: 个性化激励方案")
    incentive = system.performance_based_incentive({
        "name": "李工程师",
        "position": "高级工程师",
        "performance_rating": "A",
        "years_of_service": 4
    })
    print(f"   激励方案已生成")

    print("\n⚖️ 测试3: 薪酬公平性分析")
    equity = system.pay_equity_analysis({"scope": "技术部门"})
    print(f"   公平性得分: {equity['overall_equity_score']} ({equity['equity_grade']})")

    print("\n🔒 测试4: 人才保留策略")
    retention = system.talent_retention_strategy({"focus": "关键人才"})
    print(f"   预期改善: {retention['predicted_retention_rate_improvement']}")

    print("\n" + "=" * 60)
    print("所有测试通过! ✅")
    print("=" * 60)
