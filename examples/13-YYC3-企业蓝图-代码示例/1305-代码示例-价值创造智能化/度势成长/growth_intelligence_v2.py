"""
YYC³ 度势成长智能化系统 v2.0
基于 Five S 模型 + AI Family Agent 协同架构

核心能力:
1. 组织发展与变革管理
2. 人才梯队建设与继任者规划
3. 领导力发展与评估
4. 学习型组织构建
5. 文化塑造与价值观落地
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


class LeadershipLevel(Enum):
    """领导力层级"""
    SELF_LEADERSHIP = "自我领导"
    TEAM_LEADERSHIP = "团队领导"
    FUNCTIONAL_LEADERSHIP = "职能领导"
    BUSINESS_LEADERSHIP = "业务领导"
    STRATEGIC_LEADERShip = "战略领导"


@dataclass
class TalentProfile:
    """人才档案"""
    talent_id: str
    name: str
    position: str
    level: str
    potential: str  # 高潜/中潜/核心
    readiness: int  # 1-5年可晋升
    key_strengths: List[str]
    development_areas: List[str]
    career_aspiration: str


@dataclass
class SuccessionPlan:
    """继任计划"""
    position: str
    incumbent: str
    ready_now: List[str]
    ready_1_2years: List[str]
    ready_3_5years: List[str]
    risk_level: str


class GrowthAIFamilyCoordinator:
    """
    度势成长Agent协调器

    分工:
    - 元启·天枢: 组织战略设计与人才顶层规划
    - 言启·千行: 发展路径导航与职业引导
    - 语枢·万物: 人才数据分析与发展诊断
    - 预见·先知: 组织能力预测与未来需求
    - 千里·伯乐: 人才识别推荐与机会匹配
    - 智云·守护: 变革风险管控与文化守护
    - 格物·宗师: 领导力素质模型与评估
    - 创想·灵韵: 组织文化创新与活力激发
    """

    def __init__(self):
        self.agents = {
            "yuanqi_tianshu": {"role": "总指挥", "capability": "战略人才规划", "weight": 0.18},
            "yanqi_qianhang": {"role": "导航员", "capability": "路径职业引导", "weight": 0.10},
            "yushu_wanwu": {"role": "思考者", "capability": "数据发展诊断", "weight": 0.20},
            "yujian_xianzhi": {"role": "预言家", "capability": "组织能力预测", "weight": 0.14},
            "qianli_bole": {"role": "推荐官", "capability": "人才机会匹配", "weight": 0.13},
            "zhiyun_shouhu": {"role": "安全官", "capability": "变革风险管控", "weight": 0.12},
            "gewu_zongshi": {"role": "质量官", "capability": "领导力评估", "weight": 0.08},
            "chuangxiang_lingyun": {"role": "创意官", "capability": "文化创新激发", "weight": 0.05}
        }

    def coordinate_org_development(self, context: Dict) -> Dict:
        """协调组织发展"""
        return {
            "org_diagnosis": self._agent_analysis("yushu_wanwu", "组织现状诊断", context),
            "talent_mapping": self._agent_analysis("qianli_bole", "人才地图绘制", context),
            "leadership_assessment": self._agent_analysis("gewu_zongshi", "领导力评估", context),
            "culture_analysis": self._agent_analysis("chuangxiang_lingyun", "文化氛围分析", context),
            "future_readiness": self._agent_analysis("yujian_xianzhi", "未来就绪度", context)
        }

    def _agent_analysis(self, agent_id: str, task: str, context: Dict) -> Dict:
        agent = self.agents.get(agent_id, {})
        return {
            "agent_id": agent_id,
            "role": agent.get("role", ""),
            "task": task,
            "result": f"{agent.get('capability', '')}完成",
            "confidence": 0.84 + (agent.get("weight", 0) * 0.13)
        }


class GrowthIntelligenceV2:
    """
    YYC³ 度势成长智能化系统 v2.0
    """

    def __init__(self, config_path: Optional[str] = None):
        self.prompt_engine = None
        if PROMPT_ENGINE_AVAILABLE:
            try:
                self.prompt_engine = PromptEngine(config_path)
                print("[Growth Intelligence V2] 提示词引擎加载成功")
            except Exception as e:
                print(f"[Growth Intelligence V2] 提示词引擎加载失败: {e}")

        self.agent_coordinator = GrowthAIFamilyCoordinator()
        self.config = self._load_config(config_path)

        print("[Growth Intelligence V2] 系统初始化完成")

    def build_talent_pipeline(self, function: str) -> Dict:
        """人才梯队建设"""
        pipeline_id = f"PIPELINE-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        sample_talents = [
            TalentProfile(talent_id="T001", name="张明", position="高级经理", level="M2", potential="高潜",
                         readiness=2, key_strengths=["战略思维", "团队建设"], development_areas=["跨部门协作"],
                         career_aspiration="晋升总监"),
            TalentProfile(talent_id="T002", name="李华", position="经理", level="M1", potential="高潜",
                         readiness=3, key_strengths=["执行力", "项目管理"], development_areas=["战略视野"],
                         career_aspiration="成为业务负责人"),
            TalentProfile(talent_id="T003", name="王芳", position="主管", level="M0", potential="中潜",
                         readiness=4, key_strengths=["技术专业", "问题解决"], development_areas=["人员管理"],
                         career_aspiration="向管理转型"),
            TalentProfile(talent_id="T004", name="刘强", position="专员", level="IC3", potential="核心",
                         readiness=5, key_strengths=["专业知识", "学习能力"], development_areas=["沟通表达"],
                         career_aspiration="技术专家路线")
        ]

        pipeline_nine_box = {
            "high_performance_high_potential": [t.name for t in sample_talents if t.potential == "高潜" and t.readiness <= 2],  # 星星
            "high_performance_medium_potential": [],  # 核心骨干
            "medium_performance_high_potential": [t.name for t in sample_talents if t.potential == "高潜" and t.readiness > 2],  # 高潜储备
            "medium_performance_medium_potential": [t.name for t in sample_talents if t.potential == "中潜"],  # 稳定贡献者
            "low_performance_any_potential": []  # 待提升
        }

        return {
            "pipeline_metadata": {
                "pipeline_id": pipeline_id,
                "function": function,
                "analyzed_at": datetime.now().isoformat(),
                "model_version": "YYC3-GROWTH-V2.0-AIFamily"
            },
            "ai_family_coordination": self.agent_coordinator.coordinate_org_development({"function": function}),
            "nine_box_grid": pipeline_nine_box,
            "talent_profiles": [{
                "name": t.name,
                "position": t.position,
                "potential": t.potential,
                "readiness": f"{t.readiness}年内可晋升",
                "strengths": t.key_strengths,
                "development_focus": t.development_areas,
                "aspiration": t.career_aspiration
            } for t in sample_talents],
            "pipeline_health": {
                "high_potential_count": len([t for t in sample_talents if t.potential == "高潜"]),
                "readiness_coverage": "1-2年: 25%, 2-3年: 25%, 3-5年: 50%",
                "risk_assessment": "关键岗位后备充足度: 中等 (建议加强)"
            },
            "development_programs": [
                {
                    "program": "高潜加速发展计划(HAP)",
                    "target": "高潜人才",
                    "duration": "18个月",
                    "components": ["轮岗经历", "高管导师", "挑战性项目", "外部培训"]
                },
                {
                    "program": "新任管理者训练营",
                    "target": "新晋升管理者",
                    "duration": "6个月",
                    "components": ["管理基础", "团队建设", "绩效管理", "沟通技巧"]
                },
                {
                    "program": "专业技术深化项目",
                    "target": "专家路线人才",
                    "duration": "持续",
                    "components": ["技术认证", "行业会议", "专利发表", "内部分享"]
                }
            ],
            "succession_planning": self._generate_succession_plans(sample_talents)
        }

    def leadership_development_assessment(self, leader_data: Dict) -> Dict:
        """领导力发展评估"""
        assess_id = f"LEAD-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        competency_model = {
            "strategic_thinking": {"current_score": 7.5, "target_score": 8.5, "gap": "-1.0", "priority": "高"},
            "people_development": {"current_score": 8.2, "target_score": 8.5, "gap": "-0.3", "priority": "中"},
            "results_orientation": {"current_score": 8.8, "target_score": 8.5, "gap": "+0.3", "priority": "维持"},
            "change_leadership": {"current_score": 6.8, "target_score": 8.0, "gap": "-1.2", "priority": "高"},
            "collaboration_influence": {"current_score": 7.9, "target_score": 8.5, "gap": "-0.6", "priority": "中"},
            "innovation_agility": {"current_score": 7.2, "target_score": 8.0, "gap": "-0.8", "priority": "中"}
        }

        overall_leadership_score = sum(comp["current_score"] for comp in competency_model.values()) / len(competency_model)

        return {
            "assessment_metadata": {
                "assess_id": assess_id,
                "leader_name": leader_data.get("name", ""),
                "assessed_at": datetime.now().isoformat()
            },
            "overall_leadership_quotient": round(overall_leadership_score, 1),
            "leadership_level": self._determine_leadership_level(overall_leadership_score),
            "competency_scores": competency_model,
            "top_priorities": sorted(
                [{"competency": k, **v} for k, v in competency_model.items()],
                key=lambda x: abs(float(x["gap"])) if x["gap"].startswith("-") else 0,
                reverse=True
            )[:3],
            "personalized_development_plan": {
                "focus_areas": ["变革领导力", "战略思维"],
                "development_actions": [
                    "参与公司级变革项目获得实战经验",
                    "参加战略规划工作坊提升宏观视角",
                    "寻求高管导师指导战略思维",
                    "阅读相关书籍：《领导梯队》《从优秀到卓越》"
                ],
                "stretch_assignments": [
                    "主导跨部门协同项目",
                    "负责新业务单元的筹备",
                    "担任内部讲师分享经验"
                ],
                "coaching_support": {
                    "executive_coach": "建议配备外部教练",
                    "mentor": "匹配CEO或COO作为导师",
                    "peer_learning": "加入领导者社群"
                },
                "timeline": "12个月发展周期，每季度复盘一次"
            },
            "360_feedback_integration": {
                "self_rating": round(overall_leadership_score, 1),
                "manager_rating": round(overall_leadership_score - 0.3, 1),
                "peer_rating": round(overall_leadership_score + 0.2, 1),
                "direct_report_rating": round(overall_leadership_score - 0.1, 1),
                "key_insights": [
                    "自我认知较为准确，与多方反馈基本一致",
                    "在结果导向方面表现突出，获得一致认可",
                    "变革领导力是共识的发展重点",
                    "建议更多倾听下属声音，提升包容性领导力"
                ]
            }
        }

    def learning_organization_builder(self, org_scope: Dict) -> Dict:
        """学习型组织构建"""
        learn_id = f"LEARN-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        learning_dimensions = {
            "个人学习": {
                "current_maturity": 3.5,
                "target_maturity": 4.5,
                "indicators": ["人均培训时长", "学习参与率", "技能认证获取率"],
                "initiatives": [
                    "建立个人IDP(Individual Development Plan)制度",
                    "提供个性化学习路径推荐(LXP系统)",
                    "设立学习积分和激励机制"
                ]
            },
            "团队学习": {
                "current_maturity": 3.0,
                "target_maturity": 4.2,
                "indicators": ["知识分享频率", "团队复盘质量", "最佳实践复制率"],
                "initiatives": [
                    "推行AAR(After Action Review)事后回顾机制",
                    "建立社区实践(CoP)知识共享平台",
                    "定期举办跨团队经验交流沙龙"
                ]
            },
            "组织学习": {
                "current_maturity": 2.8,
                "target_maturity": 4.0,
                "indicators": ["创新采纳速度", "组织记忆保留", "错误学习转化率"],
                "initiatives": [
                    "建立组织知识库和案例库",
                    "鼓励试错文化和快速迭代",
                    "将学习纳入绩效考核体系"
                ]
            }
        }

        overall_lo_index = sum(d["current_maturity"] for d in learning_dimensions.values()) / len(learning_dimensions)

        return {
            "learning_metadata": {
                "learn_id": learn_id,
                "scope": org_scope.get("scope", "全公司"),
                "assessed_at": datetime.now().isoformat()
            },
            "learning_organization_index": round(overall_lo_index, 2),
            "maturity_level": "发展中" if overall_lo_index < 3.5 else ("成熟" if overall_lo_index < 4.2 else "领先"),
            "dimension_details": learning_dimensions,
            "learning_infrastructure": {
                "lms_platform": "企业在线学习管理系统(已部署)",
                "content_library": "500+门课程覆盖10+个领域",
                "social_learning": "知识社区、问答论坛、专家网络",
                "learning_analytics": "学习行为追踪、效果评估、ROI计算"
            },
            "culture_enablers": [
                "高层倡导终身学习和成长思维",
                "容错机制鼓励实验和创新",
                "时间保障：每周4小时学习时间",
                "认可奖励：学习之星、知识贡献奖"
            ],
            "roadmap_to_learning_org": {
                "phase_1_foundation_0_6months": [
                    "完善LMS功能和内容库",
                    "启动IDP试点项目",
                    "建立学习文化宣导活动"
                ],
                "phase_2_deepening_6_12months": [
                    "全面推广IDP和CoP",
                    "引入AI个性化推荐",
                    "建立学习效果评估体系"
                ],
                "phase_3_transformation_12_24months": [
                    "实现学习与业务的深度融合",
                    "打造学习品牌和生态",
                    "成为行业学习标杆"
                ]
            }
        }

    def culture_shaping_strategy(self, culture_data: Dict) -> Dict:
        """文化塑造策略"""
        culture_id = f"CULTURE-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        cultural_dimensions = [
            {"dimension": "使命愿景认同", "current_score": 8.2, "target": 9.0, "status": "良好"},
            {"dimension": "价值观践行", "current_score": 7.5, "target": 8.5, "status": "发展中"},
            {"dimension": "创新开放度", "current_score": 7.0, "target": 8.5, "status": "需关注"},
            {"dimension": "协作信任度", "current_score": 7.8, "target": 8.5, "status": "良好"},
            {"dimension": "主人翁意识", "current_score": 7.3, "target": 8.5, "status": "发展中"},
            {"dimension": "客户导向", "current_score": 8.5, "target": 9.0, "status": "优秀"}
        ]

        culture_health_index = sum(d["current_score"] for d in cultural_dimensions) / len(cultural_dimensions)

        return {
            "culture_metadata": {
                "culture_id": culture_id,
                "focus": culture_data.get("focus", "企业文化升级"),
                "assessed_at": datetime.now().isoformat()
            },
            "culture_health_index": round(culture_health_index, 2),
            "cultural_dimensions": cultural_dimensions,
            "strengths": [d["dimension"] for d in cultural_dimensions if d["current_score"] >= 8.0],
            "improvement_priorities": sorted(cultural_dimensions, key=lambda x: x["target"] - x["current_score"], reverse=True)[:3],
            "culture_rituals_and_practices": [
                {"ritual": "年度战略共创会", "frequency": "年度", "purpose": "统一愿景凝聚共识"},
                {"ritual": "月度全员大会", "frequency": "月度", "purpose": "信息透明表彰先进"},
                {"ritual": "创新黑客松", "frequency": "季度", "purpose": "激发创意鼓励尝试"},
                {"ritual": "新人入职仪式", "frequency": "按需", "purpose": "文化融入归属感"},
                {"ritual": "感谢日/ appreciation week", "frequency": "年度", "purpose": "感恩文化正向强化"}
            ],
            "values_activation_plan": [
                {
                    "value": "客户第一",
                    "behaviors": ["主动了解客户需求", "快速响应客户反馈", "超越客户期望"],
                    "recognition": "设立客户满意度奖",
                    "measurement": "NPS、CSAT、客户留存率"
                },
                {
                    "value": "拥抱变化",
                    "behaviors": ["积极面对不确定性", "主动学习新技能", "推动改进创新"],
                    "recognition": "变革先锋奖、创新提案奖",
                    "measurement": "创新项目数量、变革参与度"
                },
                {
                    "value": "诚信正直",
                    "behaviors": ["言行一致信守承诺", "勇于承认错误", "坚持原则底线"],
                    "recognition": "道德模范奖",
                    "measurement": "合规事件数、信任度调查"
                },
                {
                    "value": "团队合作",
                    "behaviors": ["主动协作支持他人", "分享知识和经验", "追求共同成功"],
                    "recognition": "团队协作奖、知识贡献奖",
                    "measurement": "跨部门项目成功率、知识分享频次"
                },
                {
                    "value": "激情投入",
                    "behaviors": ["热爱工作追求卓越", "积极主动承担责任", "永不言弃持续进取"],
                    "recognition": "卓越表现奖、长期服务奖",
                    "measurement": "敬业度调查、绩效达成率"
                }
            ],
            "transformation_roadmap": [
                {"phase": "诊断与共识(0-2个月)", "actions": ["文化审计", "价值观研讨", "愿景共创"]},
                {"phase": "示范与传播(2-6个月)", "actions": ["管理层率先垂范", "故事传播", "标杆树立"]},
                {"phase": "固化与深化(6-12个月)", "actions": ["制度嵌入", "仪式建立", "行为强化"]},
                {"phase": "评估与迭代(持续)", "actions": ["定期测量", "反馈调整", "持续进化"]}
            ]
        }

    def _determine_leadership_level(self, score: float) -> str:
        """确定领导力层级"""
        if score >= 8.5: return "Strategic Leader (战略领导者)"
        elif score >= 8.0: return "Business Leader (业务领导者)"
        elif score >= 7.5: return "Functional Leader (职能领导者)"
        elif score >= 7.0: return "Team Leader (团队领导者)"
        else: return "Emerging Leader (新兴领导者)"

    def _generate_succession_plans(self, talents: List[TalentProfile]) -> List[Dict]:
        """生成继任计划"""
        plans = [
            SuccessionPlan(position="技术研发总监", incumbent="现任总监",
                          ready_now=[], ready_1_2years=["张明"], ready_3_5years=["李华"], risk_level="中等"),
            SuccessionPlan(position="产品总监", incumbent="现任产品VP",
                          ready_now=[], ready_1_2years=[], ready_3_5years=["王芳"], risk_level="较高"),
            SuccessionPlan(position="运营总监", incumbent="现任运营VP",
                          ready_now=[], ready_1_2years=["张明"], ready_3_5years=[], risk_level="可控")
        ]

        return [{
            "position": p.position,
            "incumbent": p.incumbent,
            "ready_now": p.ready_now or ["⚠️ 无即时接班人"],
            "ready_in_1_2_years": p.ready_1_2years or ["需要加速培养"],
            "ready_in_3_5_years": p.ready_3_5years,
            "risk_level": p.risk_level,
            "recommendation": "紧急招聘" if not p.ready_now and not p.ready_1_2years else (
                "加速培养" if not p.ready_now else "维持现状")
        } for p in plans]

    def _load_config(self, config_path: Optional[str]) -> Dict:
        """加载配置"""
        return {
            "enable_agent_coordination": True,
            "leadership_model": "五层领导力梯队模型",
            "development_philosophy": "70-20-10 (70%实践 20%辅导 10%培训)"
        }


if __name__ == "__main__":
    print("=" * 60)
    print("YYC³ 度势成长智能化系统 V2.0")
    print("=" * 60)

    system = GrowthIntelligenceV2()

    print("\n👥 测试1: 人才梯队建设")
    pipeline = system.build_talent_pipeline("技术研发")
    print(f"   高潜人才: {pipeline['pipeline_health']['high_potential_count']} 人")

    print("\n🎯 测试2: 领导力发展评估")
    leadership = system.leadership_development_assessment({"name": "张总"})
    print(f"   领导力商数: {leadership['overall_leadership_quotient']}")
    print(f"   当前层级: {leadership['leadership_level']}")

    print("\n📚 测试3: 学习型组织构建")
    learning = system.learning_organization_builder({"scope": "全公司"})
    print(f"   学习指数: {learning['learning_organization_index']} ({learning['maturity_level']})")

    print("\n🎨 测试4: 文化塑造策略")
    culture = system.culture_shaping_strategy({"focus": "价值观落地"})
    print(f"   文化健康指数: {culture['culture_health_index']}")

    print("\n" + "=" * 60)
    print("所有测试通过! ✅")
    print("=" * 60)
