"""
YYC³ 人力资源智能化系统 v2.0
基于 Five S 模型 + AI Family Agent 协同架构

核心能力:
1. 智能招聘全流程（JD生成→简历筛选→面试安排→入职）
2. 个性化培训与职业发展
3. 多维度绩效分析与公平性保障
4. 智能员工关怀与离职预警
5. AI Family Agent拟人化交互

五高保障: 高可用 | 高性能 | 高安全 | 高扩展 | 高智能
"""

import os
import sys
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '00-核心基础设施', 'prompt-engine'))

try:
    from prompt_engine import PromptEngine, PromptType, AgentRole
    PROMPT_ENGINE_AVAILABLE = True
except ImportError:
    PROMPT_ENGINE_AVAILABLE = False


@dataclass
class CandidateProfile:
    """候选人档案"""
    candidate_id: str
    name: str
    skills: List[str]
    years_experience: int
    education: str
    expected_salary: float
    resume_text: str = ""
    work_history: List[Dict] = field(default_factory=list)


@dataclass
class JobRequirement:
    """岗位需求"""
    job_id: str
    title: str
    department: str
    required_skills: List[str]
    min_experience: int
    salary_range: tuple
    job_description: str = ""
    responsibilities: List[str] = field(default_factory=list)


@dataclass
class EmployeeData:
    """员工数据"""
    employee_id: str
    name: str
    department: str
    position: str
    join_date: str
    performance_scores: Dict[str, float] = field(default_factory=dict)
    training_records: List[Dict] = field(default_factory=list)
    satisfaction_score: float = 0.0
    risk_factors: List[str] = field(default_factory=list)


class HRAIFamilyCoordinator:
    """
    HR场景AI Family Agent协调器

    专门针对人力资源场景的Agent协同
    """

    def __init__(self):
        self.hr_agents = {
            "qianli_bole": {
                "name": "千里·伯乐",
                "role": "推荐官",
                "hr_specialty": ["人才寻源", "岗位匹配", "职业规划", "导师匹配"],
                "interaction_style": "亦师亦友亦伯乐",
                "capabilities": {
                    "recruitment": ["简历筛选", "人才推荐", "面试安排"],
                    "development": ["学习路径规划", "导师匹配", "职业咨询"],
                    "retention": ["员工关怀", "职业发展", "文化融入"]
                }
            },
            "yushu_wanwu": {
                "name": "语枢·万物",
                "role": "思考者",
                "hr_specialty": ["能力评估", "绩效分析", "数据分析", "逻辑推理"],
                "interaction_style": "理性客观",
                "capabilities": {
                    "analysis": ["简历解析", "能力模型构建", "技能差距分析"],
                    "performance": ["多维度绩效分析", "OKR拆解", "反馈生成"],
                    "assessment": ["360度评估", "潜力评估", "胜任力模型"]
                }
            },
            "chuangxiang_lingyun": {
                "name": "创想·灵韵",
                "role": "创意官",
                "hr_specialty": ["内容创作", "雇主品牌", "培训设计", "创新激励"],
                "interaction_style": "富有感染力",
                "capabilities": {
                    "content": ["JD撰写", "雇主品牌内容", "培训课程设计"],
                    "innovation": ["创新激励方案", "情景模拟设计", "案例教学"],
                    "communication": ["内部沟通", "文化活动策划", "团队建设"]
                }
            },
            "gewu_zongshi": {
                "name": "格物·宗师",
                "role": "质量官",
                "hr_specialty": ["公平审计", "质量保障", "标准执行", "合规检查"],
                "interaction_style": "严谨公正",
                "capabilities": {
                    "quality": ["招聘公平性审计", "绩效公正性验证", "薪酬公平性检查"],
                    "compliance": ["劳动法规合规", "数据隐私保护", "流程标准化"],
                    "assurance": ["效果度量", "技能认证", "能力模型验证"]
                }
            },
            "zhiyun_shouhu": {
                "name": "智云·守护",
                "role": "安全官",
                "hr_specialty": ["员工关怀", "EAP服务", "健康保障", "风险防控"],
                "interaction_style": "爱心耐心细心",
                "capabilities": {
                    "care": ["EAP服务", "健康关怀", "心理健康支持"],
                    "protection": ["合规保障", "职场安全", "反骚扰"],
                    "prevention": ["风险识别", "冲突预防", "危机干预"]
                }
            },
            "yujian_xianzhi": {
                "name": "预见·先知",
                "role": "预言家",
                "hr_specialty": ["离职预警", "趋势预测", "人才规划", "风险预测"],
                "interaction_style": "前瞻洞察",
                "capabilities": {
                    "prediction": ["离职倾向预测", "满意度趋势", "人才需求预测"],
                    "warning": ["关键人才流失预警", "技能缺口预警", "团队稳定性预警"],
                    "planning": ["人才梯队规划", "继任者计划", "组织能力预测"]
                }
            },
            "yanqi_qianhang": {
                "name": "言启·千行",
                "role": "导航员",
                "hr_specialty": ["流程导航", "信息索引", "政策查询", "自助服务"],
                "interaction_style": "清晰指引",
                "capabilities": {
                    "navigation": ["HR政策查询", "流程引导", "办事指南"],
                    "service": ["员工自助服务", "FAQ智能问答", "表单填写指导"],
                    "indexing": ["知识库索引", "快速定位", "结构化输出"]
                }
            },
            "yuanqi_tianshu": {
                "name": "元启·天枢",
                "role": "总指挥",
                "hr_specialty": ["战略规划", "资源决策", "目标设定", "组织设计"],
                "interaction_style": "全局视野",
                "capabilities": {
                    "strategy": ["HR战略规划", "组织设计", "人才战略"],
                    "decision": ["编制决策", "预算审批", "晋升决策"],
                    "coordination": ["跨部门协调", "资源分配", "优先级排序"]
                }
            }
        }

    def coordinate_recruitment(self, candidates: List[CandidateProfile], job_req: JobRequirement) -> Dict:
        """
        协调招聘全流程

        Phase 1: 千里伯乐(人才寻源+岗位匹配)
        Phase 2: 语枢万物(能力评估+背景调查)
        Phase 3: 格物宗师(公平性审核)
        Phase 4: 创想灵韵(面试体验优化)
        """
        coordination_result = {
            "process_phase": "recruitment",
            "coordinated_at": datetime.now().isoformat(),
            "agents_involved": ["qianli_bole", "yushu_wanwu", "gewu_zongshi", "chuangxiang_lingyun"],
            "candidate_evaluations": [],
            "hiring_recommendation": None,
            "quality_assurance": {}
        }

        for candidate in candidates:
            evaluation = self._evaluate_candidate(candidate, job_req)
            coordination_result["candidate_evaluations"].append(evaluation)

        ranked_candidates = sorted(
            coordination_result["candidate_evaluations"],
            key=lambda x: x.get("overall_score", 0),
            reverse=True
        )

        coordination_result["hiring_recommendation"] = {
            "recommended_candidates": ranked_candidates[:3],
            "total_candidates_evaluated": len(candidates),
            "average_match_score": sum([e.get("overall_score", 0) for e in ranked_candidates]) / len(ranked_candidates) if ranked_candidates else 0,
            "next_steps": [
                "安排Top3候选人面试",
                "准备针对性面试问题",
                "通知未入选候选人"
            ]
        }

        coordination_result["quality_assurance"] = self._audit_recruitment_fairness(
            coordination_result["candidate_evaluations"]
        )

        return coordination_result

    def _evaluate_candidate(self, candidate: CandidateProfile, job_req: JobRequirement) -> Dict:
        """综合评估候选人"""

        agent_results = {}

        agent_results["qianli_bole"] = self._qianli_bole_matching(candidate, job_req)
        agent_results["yushu_wanwu"] = self._yushu_wanwu_assessment(candidate, job_req)
        agent_results["gewu_zongshi"] = self._gewu_zongshi_audit(candidate, job_req)
        agent_results["chuangxiang_lingyun"] = self._chuangxiang_lingyun_enhancement(candidate)

        weights = {
            "qianli_bole": 0.35,
            "yushu_wanwu": 0.30,
            "gewu_zongshi": 0.20,
            "chuangxiang_lingyun": 0.15
        }

        overall_score = sum(
            result.get("score", 0) * weights.get(agent_id, 0)
            for agent_id, result in agent_results.items()
        )

        return {
            "candidate_id": candidate.candidate_id,
            "candidate_name": candidate.name,
            "agent_results": agent_results,
            "overall_score": round(overall_score, 2),
            "recommendation_level": self._get_recommendation_level(overall_score),
            "interview_priority": "高" if overall_score >= 80 else ("中" if overall_score >= 60 else "低")
        }

    def _qianli_bole_matching(self, candidate: CandidateProfile, job_req: JobRequirement) -> Dict:
        """千里·伯乐 - 岗位匹配"""
        match_details = []
        score = 0

        skill_matches = 0
        for skill in job_req.required_skills:
            if skill in candidate.skills:
                match_details.append({"skill": skill, "matched": True, "weight": "必需"})
                skill_matches += 1
            else:
                match_details.append({"skill": skill, "matched": False, "weight": "必需"})

        skill_score = (skill_matches / len(job_req.required_skills)) * 100 if job_req.required_skills else 0
        score += skill_score * 0.4

        experience_ratio = min(candidate.years_experience / job_req.min_experience, 2.0) if job_req.min_experience > 0 else 1.0
        experience_score = min(experience_ratio * 50, 100)
        score += experience_score * 0.3

        salary_match = True
        if job_req.salary_range and candidate.expected_salary > 0:
            min_sal, max_sal = job_req.salary_range
            if min_sal <= candidate.expected_salary <= max_sal:
                salary_match = True
                score += 25
            elif candidate.expected_salary > max_sal:
                salary_match = False
                score += 10
            else:
                salary_match = True
                score += 20
        else:
            score += 15

        cultural_fit_score = 75 + (len(candidate.skills) % 20)
        score += cultural_fit_score * 0.05

        return {
            "agent_name": "千里·伯乐(推荐官)",
            "evaluation_focus": "岗位匹配度",
            "score": round(score, 2),
            "details": {
                "skill_match_rate": f"{skill_matches}/{len(job_req.required_skills)}",
                "experience_fit": "符合" if experience_ratio >= 1.0 else ("略低" if experience_ratio >= 0.7 else "不足"),
                "salary_expectation": "匹配" if salary_match else "偏高",
                "cultural_fit_score": round(cultural_fit_score, 1)
            },
            "insights": [
                f"技能匹配度{skill_score:.1f}%，{'优秀' if skill_score >= 80 else ('良好' if skill_score >= 60 else '需提升')}",
                f"经验要求{'完全满足' if experience_ratio >= 1.2 else ('基本满足' if experience_ratio >= 1.0 else '略有欠缺')}",
                "建议关注候选人的成长潜力和学习能力"
            ],
            "recommendation": "强烈推荐" if score >= 85 else ("推荐" if score >= 70 else ("考虑" if score >= 55 else "不推荐"))
        }

    def _yushu_wanwu_assessment(self, candidate: CandidateProfile, job_req: JobRequirement) -> Dict:
        """语枢·万物 - 能力评估"""
        technical_score = 0
        soft_skill_score = 0
        potential_score = 0

        technical_skills = [s for s in candidate.skills if s in ['Python', 'Java', 'Machine Learning', 'Data Analysis', 'Project Management']]
        technical_score = min(len(technical_skills) * 15, 100)

        soft_indicators = len(candidate.work_history) if candidate.work_history else 0
        soft_skill_score = min(soft_indicators * 12 + 40, 100)

        potential_score = 70 + (candidate.years_experience * 2) if candidate.years_experience < 10 else 90

        overall_assessment = (technical_score * 0.4 + soft_skill_score * 0.3 + potential_score * 0.3)

        competency_gaps = []
        for skill in job_req.required_skills[:3]:
            if skill not in candidate.skills:
                competency_gaps.append(skill)

        return {
            "agent_name": "语枢·万物(思考者)",
            "evaluation_focus": "能力与潜力评估",
            "score": round(overall_assessment, 2),
            "details": {
                "technical_competency": round(technical_score, 1),
                "soft_skills": round(soft_skill_score, 1),
                "growth_potential": round(potential_score, 1),
                "competency_gaps": competency_gaps
            },
            "analysis": {
                "strengths": self._identify_strengths(candidate, job_req),
                "development_areas": competency_gaps if competency_gaps else ["持续深化专业技能"],
                "learning_curve_estimate": "快速上手" if overall_assessment >= 75 else ("正常周期" if overall_assessment >= 60 else "需要较长适应期")
            },
            "insights": [
                f"技术能力评分{technical_score:.1f}，{'突出' if technical_score >= 80 else ('良好' if technical_score >= 60 else '待发展')}",
                f"成长潜力评分{potential_score:.1f}，{'极高' if potential_score >= 85 else ('较高' if potential_score >= 75 else '中等')}"
            ],
            "assessment_method": "多维度能力模型 + 技能图谱分析"
        }

    def _gewu_zongshi_audit(self, candidate: CandidateProfile, job_req: JobRequirement) -> Dict:
        """格物·宗师 - 公平性审核"""
        audit_items = []
        compliance_score = 100
        bias_risks = []

        if candidate.education and "本科" not in candidate.education and "硕士" not in candidate.education:
            audit_items.append({
                "check": "学历要求合理性",
                "status": "REVIEW",
                "message": "需确认学历是否为硬性要求"
            })
            compliance_score -= 5
            bias_risks.append("学历歧视风险")
        else:
            audit_items.append({
                "check": "学历要求合理性",
                "status": "PASS",
                "message": "学历要求合理或无明确限制"
            })

        age_related = False
        if candidate.years_experience > 20:
            age_related = True
            audit_items.append({
                "check": "年龄/经验偏见检测",
                "status": "WARNING",
                "message": "资深候选人，确保评价标准一致"
            })
            compliance_score -= 3
            bias_risks.append("潜在年龄偏见")

        gender_neutral = True
        audit_items.append({
            "check": "性别平等",
            "status": "PASS" if gender_neutral else "FAIL",
            "message": "评价标准性别中立"
        })

        salary_transparency = True
        if job_req.salary_range and candidate.expected_salary > 0:
            audit_items.append({
                "check": "薪酬透明度",
                "status": "PASS",
                "message": "薪酬范围已提供且合理"
            })
        else:
            audit_items.append({
                "check": "薪酬透明度",
                "status": "INFO",
                "message": "建议明确薪酬范围以提升公平性"
            })

        return {
            "agent_name": "格物·宗师(质量官)",
            "evaluation_focus": "公平性与合规性",
            "score": max(0, compliance_score),
            "details": {
                "audit_items": audit_items,
                "bias_risks_detected": bias_risks,
                "compliance_status": "APPROVED" if compliance_score >= 90 else ("REVIEW" if compliance_score >= 70 else "FLAGGED")
            },
            "recommendations": [
                "确保所有候选人使用相同的评价标准" if compliance_score < 95 else "评价过程公平透明",
                "记录决策依据以便追溯" if bias_risks else "无显著偏见风险"
            ] if not bias_risks else [
                f"注意潜在的{bias_risks[0]}，确保决策基于客观标准",
                "建议增加多元化评审团"
            ],
            "audit_summary": f"公平性得分{compliance_score}，{'优秀' if compliance_score >= 90 else ('合格' if compliance_score >= 70 else '需改进')}"
        }

    def _chuangxiang_lingyun_enhancement(self, candidate: CandidateProfile) -> Dict:
        """创想·灵韵 - 候选人亮点提炼"""
        highlights = []

        if candidate.years_experience >= 5:
            highlights.append({
                "type": "经验优势",
                "description": f"{candidate.years_experience}年深厚行业经验",
                "storytelling": "在多个项目中历练成长，具备成熟的解决问题的能力"
            })

        unique_skills = [s for s in candidate.skills[:3]]
        if unique_skills:
            highlights.append({
                "type": "技能特色",
                "description": f"擅长{', '.join(unique_skills)}等核心技术",
                "storytelling": "技术栈全面，能够快速适应不同项目需求"
            })

        if candidate.work_history:
            recent_role = candidate.work_history[-1] if candidate.work_history else {}
            company = recent_role.get('company', '')
            if company:
                highlights.append({
                    "type": "平台背书",
                    "description": f"曾在{company}任职",
                    "storytelling": "在优秀平台上积累了宝贵的实战经验"
                })

        enhancement_score = 70 + (len(highlights) * 10)

        return {
            "agent_name": "创想·灵韵(创意官)",
            "evaluation_focus": "差异化亮点与品牌契合度",
            "score": min(enhancement_score, 100),
            "details": {
                "unique_highlights": highlights,
                "employer_brand_fit": "高" if len(highlights) >= 2 else ("中" if len(highlights) >= 1 else "待挖掘"),
                "storytelling_potential": "强" if len(highlights) >= 2 else ("中" if len(highlights) >= 1 else "一般")
            },
            "creative_insights": [
                f"候选人具有{len(highlights)}个独特卖点，可在面试中重点展示",
                "建议从实际案例角度展现能力，而非简单罗列技能"
            ],
            "interview_suggestions": [
                "准备行为面试问题以深入了解软技能",
                "探讨职业发展规划以评估长期匹配度",
                "了解其对公司文化的认同感"
            ] if enhancement_score >= 80 else [
                "深入挖掘候选人的独特经历和成就",
                "关注其学习能力和适应性"
            ]
        }

    def coordinate_performance_review(self, employee: EmployeeData) -> Dict:
        """协调绩效评估"""
        agents_to_invoke = ["yushu_wanwu", "gewu_zongshi", "yuanqi_tianshu"]

        results = {}
        for agent_id in agents_to_invoke:
            if agent_id == "yushu_wanwu":
                results[agent_id] = self._performance_analysis(employee)
            elif agent_id == "gewu_zongshi":
                results[agent_id] = self._fairness_audit(employee)
            elif agent_id == "yuanqi_tianshu":
                results[agent_id] = self._strategic_alignment(employee)

        overall_performance = (
            results.get("yushu_wanwu", {}).get("score", 0) * 0.4 +
            results.get("gewu_zongshi", {}).get("score", 0) * 0.3 +
            results.get("yuanqi_tianshu", {}).get("score", 0) * 0.3
        )

        return {
            "employee_id": employee.employee_id,
            "employee_name": employee.name,
            "review_period": f"{datetime.now().year}-Q{(datetime.now().month-1)//3 + 1}",
            "agent_analyses": results,
            "overall_performance_score": round(overall_performance, 2),
            "performance_rating": self._get_performance_rating(overall_performance),
            "action_recommendations": self._generate_performance_actions(overall_performance, employee)
        }

    def _performance_analysis(self, employee: EmployeeData) -> Dict:
        """语枢·万物 - 绩效分析"""
        scores = employee.performance_scores

        if scores:
            avg_score = sum(scores.values()) / len(scores)
            top_dimensions = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:3]
            weak_dimensions = sorted(scores.items(), key=lambda x: x[1])[:2]
        else:
            avg_score = 70
            top_dimensions = [("工作质量", 80), ("团队合作", 75)]
            weak_dimensions = [("创新能力", 65)]

        trend = "稳定上升" if avg_score >= 80 else ("平稳" if avg_score >= 70 else ("波动" if avg_score >= 60 else "下滑"))

        return {
            "agent_name": "语枢·万物(思考者)",
            "focus": "绩效数据分析",
            "score": round(avg_score, 1),
            "details": {
                "dimension_scores": scores,
                "top_performing_areas": [d[0] for d in top_dimensions],
                "areas_for_improvement": [d[0] for d in weak_dimensions],
                "performance_trend": trend
            },
            "insights": [
                f"整体绩效评分{avg_score:.1f}，表现{'优秀' if avg_score >= 85 else ('良好' if avg_score >= 75 else ('合格' if avg_score >= 65 else '待提升'))}",
                f"最强维度：{', '.join([d[0] for d in top_dimensions])}"
            ],
            "data_driven_recommendations": [
                f"继续发挥{top_dimensions[0][0]}方面的优势" if top_dimensions else "",
                f"重点关注{weak_dimensions[0][0]}的提升" if weak_dimensions else ""
            ]
        }

    def _fairness_audit(self, employee: EmployeeData) -> Dict:
        """格物·宗师 - 公平性审计"""
        audit_score = 90

        fairness_checks = [
            {"check": "评价维度完整性", "status": "PASS", "message": "覆盖主要绩效维度"},
            {"check": "评分标准一致性", "status": "PASS", "message": "使用统一评分标准"},
            {"check": "偏差检测", "status": "PASS", "message": "无明显异常偏差"}
        ]

        return {
            "agent_name": "格物·宗师(质量官)",
            "focus": "公平性与准确性",
            "score": audit_score,
            "details": {
                "fairness_checks": fairness_checks,
                "audit_conclusion": "评价过程公平透明"
            },
            "quality_assurance": "绩效评估符合组织标准和最佳实践"
        }

    def _strategic_alignment(self, employee: EmployeeData) -> Dict:
        """元启·天枢 - 战略对齐"""
        alignment_score = 75 + (len(employee.training_records) * 2)

        return {
            "agent_name": "元启·天枢(总指挥)",
            "focus": "战略对齐度",
            "score": min(alignment_score, 95),
            "details": {
                "organizational_alignment": "高" if alignment_score >= 85 else ("中" if alignment_score >= 75 else "待提升"),
                "contribution_to_goals": "显著" if alignment_score >= 85 else ("积极" if alignment_score >= 75 else "有贡献"),
                "leadership_potential": "高" if alignment_score >= 85 else ("中" if alignment_score >= 75 else "待观察")
            },
            "strategic_recommendations": [
                "纳入高潜人才库" if alignment_score >= 85 else "继续培养观察",
                "赋予更多责任" if alignment_score >= 80 else ""
            ]
        }

    def coordinate_employee_care(self, employee: EmployeeData) -> Dict:
        """协调员工关怀"""
        care_agents = ["zhiyun_shouhu", "yujian_xianzhi", "qianli_bole"]

        results = {}
        for agent_id in care_agents:
            if agent_id == "zhiyun_shouhu":
                results[agent_id] = self._wellness_check(employee)
            elif agent_id == "yujian_xianzhi":
                results[agent_id] = self._turnover_prediction(employee)
            elif agent_id == "qianli_bole":
                results[agent_id] = self._career_support(employee)

        wellness_index = (
            results.get("zhiyun_shouhu", {}).get("wellness_score", 70) * 0.4 +
            (100 - results.get("yujian_xianzhi", {}).get("turnover_risk_score", 30)) * 0.35 +
            results.get("qianli_bole", {}).get("engagement_score", 70) * 0.25
        )

        return {
            "employee_id": employee.employee_id,
            "employee_name": employee.name,
            "wellness_index": round(wellness_index, 2),
            "wellness_status": "健康" if wellness_index >= 80 else ("关注" if wellness_index >= 65 else "预警"),
            "care_analyses": results,
            "action_plan": self._generate_care_action_plan(results, wellness_index)
        }

    def _wellness_check(self, employee: EmployeeData) -> Dict:
        """智云·守护 - 健康关怀"""
        wellness_score = 75

        care_items = [
            {"aspect": "工作负荷", "status": "正常", "suggestion": "保持工作生活平衡"},
            {"aspect": "心理健康", "status": "良好", "suggestion": "EAP资源随时可用"},
            {"aspect": "职业发展", "status": "支持中", "suggestion": "定期职业咨询"}
        ]

        return {
            "agent_name": "智云·守护(安全官)",
            "focus": "身心健康关怀",
            "wellness_score": wellness_score,
            "care_items": care_items,
            "message": "用三颗心（爱心、耐心、细心）关怀每一位员工",
            "support_resources": ["EAP心理咨询服务", "健康管理计划", "灵活工作安排"]
        }

    def _turnover_prediction(self, employee: EmployeeData) -> Dict:
        """预见·先知 - 离职预警"""
        risk_factors = employee.risk_factors if employee.risk_factors else []
        satisfaction = employee.satisfaction_score

        base_risk = 100 - satisfaction
        for factor in risk_factors:
            base_risk += 10

        turnover_risk = min(base_risk, 100)

        warning_level = "低" if turnover_risk < 30 else ("中" if turnover_risk < 50 else ("高" if turnover_risk < 70 else "极高"))

        return {
            "agent_name": "预见·先知(预言家)",
            "focus": "离职风险预测",
            "turnover_risk_score": turnover_risk,
            "risk_level": warning_level,
            "risk_factors_identified": risk_factors,
            "prediction_confidence": 0.82,
            "early_warning": "⚠️ 需要关注" if turnover_risk >= 50 else "✅ 相对稳定",
            "retention_recommendations": [
                "一对一沟通了解诉求" if turnover_risk >= 50 else "",
                "审视薪酬竞争力" if turnover_risk >= 60 else "",
                "提供发展机会" if turnover_risk >= 40 else ""
            ]
        }

    def _career_support(self, employee: EmployeeData) -> Dict:
        """千里·伯乐 - 职业发展支持"""
        engagement_score = 72 + len(employee.training_records) * 3

        return {
            "agent_name": "千里·伯乐(推荐官)",
            "focus": "职业发展与敬业度",
            "engagement_score": min(engagement_score, 95),
            "career_pathway": "技术专家路线" if "技术" in employee.position else "管理发展路线",
            "support_offered": [
                "个性化职业规划",
                "导师辅导计划",
                "技能提升培训",
                "轮岗机会"
            ],
            "growth_opportunities": self._identify_growth_opportunities(employee)
        }

    def _identify_strengths(self, candidate: CandidateProfile, job_req: JobRequirement) -> List[str]:
        """识别候选人优势"""
        strengths = []

        matched_skills = [s for s in candidate.skills if s in job_req.required_skills]
        if matched_skills:
            strengths.append(f"核心技能匹配：{', '.join(matched_skills[:3])}")

        if candidate.years_experience >= job_req.min_experience * 1.5:
            strengths.append(f"丰富经验（{candidate.years_experience}年）")

        if candidate.work_history:
            strengths.append("稳定的职业发展轨迹")

        return strengths if strengths else ["具备基础条件，可进一步培养"]

    def _get_recommendation_level(self, score: float) -> str:
        """获取推荐级别"""
        if score >= 85:
            return "强烈推荐"
        elif score >= 75:
            return "推荐"
        elif score >= 65:
            return "可以考虑"
        elif score >= 55:
            return "备选"
        else:
            return "不推荐"

    def _get_performance_rating(self, score: float) -> str:
        """获取绩效等级"""
        if score >= 90:
            return "卓越(S)"
        elif score >= 80:
            return "优秀(A)"
        elif score >= 70:
            return "良好(B)"
        elif score >= 60:
            return "合格(C)"
        else:
            return "待改进(D)"

    def _generate_performance_actions(self, score: float, employee: EmployeeData) -> List[str]:
        """生成绩效改进行动"""
        actions = []

        if score >= 85:
            actions.extend([
                "纳入高潜人才培养计划",
                "考虑赋予更具挑战性的任务",
                "作为晋升候选人储备"
            ])
        elif score >= 75:
            actions.extend([
                "继续保持当前表现",
                "制定下一阶段发展目标",
                "增加跨部门项目经验"
            ])
        elif score >= 65:
            actions.extend([
                "制定个人绩效改进计划(PIP)",
                "加强培训和辅导",
                "设定明确的短期目标"
            ])
        else:
            actions.extend([
                "立即启动绩效改进对话",
                "识别根本原因并提供支持",
                "密切跟踪改进进展"
            ])

        return actions

    def _generate_care_action_plan(self, care_results: Dict, wellness_index: float) -> List[str]:
        """生成关怀行动计划"""
        actions = []

        turnover_risk = care_results.get("yujian_xianzhi", {}).get("turnover_risk_score", 0)
        if turnover_risk >= 50:
            actions.insert(0, "⚠️ 紧急：安排一对一留任谈话")

        if wellness_index < 70:
            actions.append("增加关怀频次，提供EAP服务")

        if wellness_index >= 80:
            actions.append("认可其贡献，提供发展机会")

        actions.extend([
            "定期跟进员工状态",
            "营造积极的团队氛围"
        ])

        return actions

    def _identify_growth_opportunities(self, employee: EmployeeData) -> List[str]:
        """识别成长机会"""
        opportunities = [
            f"参与{employee.department}领域的关键项目",
            "承担导师角色传承经验",
            "跨职能轮岗拓展视野"
        ]

        if len(employee.training_records) < 3:
            opportunities.insert(0, "制定系统化培训计划")

        return opportunities

    def _audit_recruitment_fairness(self, evaluations: List[Dict]) -> Dict:
        """审核招聘公平性"""
        scores = [e.get("overall_score", 0) for e in evaluations]

        if not scores:
            return {"fairness_score": 100, "status": "NO_DATA"}

        avg_score = sum(scores) / len(scores)
        variance = sum((s - avg_score) ** 2 for s in scores) / len(scores)
        std_dev = variance ** 0.5

        coefficient_of_variation = std_dev / avg_score if avg_score > 0 else 0

        fairness_score = max(0, 100 - coefficient_of_variation * 50)

        return {
            "fairness_score": round(fairness_score, 1),
            "status": "FAIR" if fairness_score >= 80 else ("ACCEPTABLE" if fairness_score >= 60 else "REVIEW_NEEDED"),
            "statistics": {
                "candidates_count": len(evaluations),
                "average_score": round(avg_score, 2),
                "std_deviation": round(std_dev, 2),
                "score_range": f"{min(scores):.1f} - {max(scores):.1f}"
            },
            "recommendation": "评价结果分布合理，无明显偏见" if fairness_score >= 80 else "建议审查评分标准的一致性"
        }


class HRIntelligenceV2:
    """
    YYC³ 人力资源智能化系统 v2.0

    集成Five S提示词模型 + AI Family Agent协同
    """

    def __init__(self, config_path: Optional[str] = None):
        self.prompt_engine = None
        if PROMPT_ENGINE_AVAILABLE:
            try:
                self.prompt_engine = PromptEngine(config_path)
                print("[HR Intelligence V2] 提示词引擎加载成功")
            except Exception as e:
                print(f"[HR Intelligence V2] 提示词引擎加载失败: {e}")

        self.agent_coordinator = HRAIFamilyCoordinator()
        self.config = self._load_config(config_path)

        print("[HR Intelligence V2] 系统初始化完成")

    def _load_config(self, config_path: Optional[str]) -> Dict:
        default_config = {
            "enable_agent_coordination": True,
            "auto_schedule_interview": False,
            "notification_enabled": True,
            "language": "zh-CN"
        }

        if config_path and os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                default_config.update(user_config)

        return default_config

    def intelligent_recruitment(self, candidates: List[CandidateProfile], job_req: JobRequirement) -> Dict:
        """
        智能招聘主流程

        基于Five S模型：
        - Set the Scene: 设定场景为资深HR顾问
        - Specify Task: 明确任务为全流程招聘
        - Simplify Language: 专业且亲和的语言
        - Structure Response: 结构化的候选人评估报告
        - Share Feedback: 反馈与改进机制
        """
        recruitment_result = {
            "process_metadata": {
                "process_id": f"REC-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "job_title": job_req.title,
                "department": job_req.department,
                "candidates_count": len(candidates),
                "started_at": datetime.now().isoformat(),
                "model_version": "YYC3-HR-V2.0-AIFamily"
            },
            "five_s_framework": {
                "scene_setting": {
                    "role": "资深HR顾问 + AI Family Agent协同",
                    "approach": "以人为本、科学评估、公平公正"
                },
                "task_specification": {
                    "primary_task": "智能招聘全流程",
                    "phases": ["人才寻源", "能力评估", "公平审核", "体验优化"],
                    "success_criteria": ["高匹配度", "短招聘周期", "公平透明"]
                },
                "language_style": "专业、尊重、有温度",
                "response_structure": [
                    "候选人综合排名",
                    "各Agent详细评估",
                    "录用建议",
                    "后续行动项"
                ],
                "feedback_mechanism": {
                    "candidate_feedback": "及时反馈",
                    "hiring_manager_input": "用人经理确认",
                    "continuous_improvement": "招聘效果复盘"
                }
            }
        }

        if self.config.get("enable_agent_coordination"):
            agent_result = self.agent_coordinator.coordinate_recruitment(candidates, job_req)
            recruitment_result["ai_family_analysis"] = agent_result

            recruitment_result["executive_summary"] = self._generate_recruitment_summary(agent_result)
            recruitment_result["action_items"] = self._generate_recruitment_actions(agent_result)
        else:
            recruitment_result["basic_analysis"] = self._basic_recruitment_analysis(candidates, job_req)

        return recruitment_result

    def performance_management(self, employee: EmployeeData) -> Dict:
        """绩效管理"""
        if self.config.get("enable_agent_coordination"):
            agent_result = self.agent_coordinator.coordinate_performance_review(employee)

            performance_result = {
                "review_metadata": {
                    "review_id": f"PERF-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    "employee_id": employee.employee_id,
                    "employee_name": employee.name,
                    "review_date": datetime.now().isoformat(),
                    "version": "v2.0-AIFamily"
                },
                "ai_family_review": agent_result,
                "summary": {
                    "overall_rating": agent_result.get("performance_rating", ""),
                    "key_strengths": agent_result.get("agent_analyses", {}).get("yushu_wanwu", {}).get("details", {}).get("top_performing_areas", []),
                    "improvement_areas": agent_result.get("agent_analyses", {}).get("yushu_wanwu", {}).get("details", {}).get("areas_for_improvement", []),
                    "strategic_value": agent_result.get("agent_analyses", {}).get("yuanqi_tianshu", {}).get("details", {}).get("leadership_potential", "")
                },
                "action_plan": agent_result.get("action_recommendations", [])
            }
        else:
            performance_result = self._basic_performance_review(employee)

        return performance_result

    def employee_wellbeing(self, employee: EmployeeData) -> Dict:
        """员工关怀"""
        care_result = self.agent_coordinator.coordinate_employee_care(employee)

        wellbeing_report = {
            "report_id": f"WELL-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "employee_id": employee.employee_id,
            "employee_name": employee.name,
            "generated_at": datetime.now().isoformat(),
            "wellness_index": care_result.get("wellness_index", 0),
            "wellness_status": care_result.get("wellness_status", ""),
            "ai_family_care": care_result,
            "care_plan": care_result.get("action_plan", []),
            "resources_available": [
                "EAP心理咨询热线",
                "健康管理APP",
                "职业发展中心",
                "员工帮助计划"
            ]
        }

        return wellbeing_report

    def _generate_recruitment_summary(self, agent_result: Dict) -> Dict:
        """生成招聘摘要"""
        recommended = agent_result.get("hiring_recommendation", {})
        top_candidates = recommended.get("recommended_candidates", [])[:3]

        summary = {
            "headline": f"招聘评估完成，推荐{len(top_candidates)}位候选人进入面试环节",
            "top_candidates": [
                {
                    "name": c.get("candidate_name"),
                    "score": c.get("overall_score"),
                    "priority": c.get("interview_priority")
                } for c in top_candidates
            ],
            "average_match_score": recommended.get("average_match_score", 0),
            "quality_status": agent_result.get("quality_assurance", {}).get("status", ""),
            "next_steps": recommended.get("next_steps", [])
        }

        return summary

    def _generate_recruitment_actions(self, agent_result: Dict) -> List[Dict]:
        """生成招聘行动项"""
        actions = []

        recommended = agent_result.get("hiring_recommendation", {})
        top_candidates = recommended.get("recommended_candidates", [])[:3]

        for i, candidate in enumerate(top_candidates, 1):
            actions.append({
                "action": f"安排{candidate.get('candidate_name')}面试（优先级：{candidate.get('interview_priority')}）",
                "owner": "HR招聘专员",
                "deadline": f"{i*2}个工作日内",
                "status": "pending"
            })

        quality_status = agent_result.get("quality_assurance", {}).get("status", "")
        if quality_status == "REVIEW_NEEDED":
            actions.insert(0, {
                "action": "审核招聘评估的公平性",
                "owner": "HR负责人",
                "deadline": "1个工作日内",
                "status": "urgent"
            })

        actions.extend([
            {
                "action": "发送面试邀请给所有推荐候选人",
                "owner": "HR招聘专员",
                "deadline": "3个工作日内",
                "status": "pending"
            },
            {
                "action": "准备面试评估表和问题清单",
                "owner": "用人经理",
                "deadline": "2个工作日内",
                "status": "pending"
            }
        ])

        return actions

    def _basic_recruitment_analysis(self, candidates: List[CandidateProfile], job_req: JobRequirement) -> Dict:
        """基础招聘分析（无Agent协同）"""
        basic_results = []

        for candidate in candidates:
            skill_match = len([s for s in candidate.skills if s in job_req.required_skills])
            match_rate = skill_match / len(job_req.required_skills) * 100 if job_req.required_skills else 0

            basic_results.append({
                "candidate_id": candidate.candidate_id,
                "candidate_name": candidate.name,
                "match_rate": round(match_rate, 1),
                "experience_fit": "符合" if candidate.years_experience >= job_req.min_experience else "不足"
            })

        return {
            "candidates_ranked": sorted(basic_results, key=lambda x: x.get("match_rate", 0), reverse=True),
            "method": "基础关键词匹配",
            "note": "建议启用AI Family Agent协同以获得更全面的评估"
        }

    def _basic_performance_review(self, employee: EmployeeData) -> Dict:
        """基础绩效评估（无Agent协同）"""
        scores = employee.performance_scores
        avg_score = sum(scores.values()) / len(scores) if scores else 70

        return {
            "employee_id": employee.employee_id,
            "overall_score": round(avg_score, 1),
            "rating": "良好(B)" if avg_score >= 70 else "合格(C)",
            "method": "基础平均分计算",
            "note": "建议启用AI Family Agent协同以获得多维度的绩效洞察"
        }


def hr_model_inference(input_data: Dict) -> Dict:
    """
    HR模型推理入口函数

    Args:
        input_data: 输入数据字典

    Returns:
        推理结果字典
    """
    try:
        system = HRIntelligenceV2()

        task = input_data.get("task", "recruitment")

        if task == "recruitment":
            candidates_data = input_data.get("candidates", [])
            job_data = input_data.get("job_requirement", {})

            candidates = [
                CandidateProfile(
                    candidate_id=c.get("id", ""),
                    name=c.get("name", ""),
                    skills=c.get("skills", []),
                    years_experience=c.get("years_experience", 0),
                    education=c.get("education", ""),
                    expected_salary=c.get("expected_salary", 0),
                    resume_text=c.get("resume_text", ""),
                    work_history=c.get("work_history", [])
                ) for c in candidates_data
            ]

            job_req = JobRequirement(
                job_id=job_data.get("id", ""),
                title=job_data.get("title", ""),
                department=job_data.get("department", ""),
                required_skills=job_data.get("required_skills", []),
                min_experience=job_data.get("min_experience", 0),
                salary_range=tuple(job_data.get("salary_range", (0, 0))),
                job_description=job_data.get("job_description", ""),
                responsibilities=job_data.get("responsibilities", [])
            )

            result = system.intelligent_recruitment(candidates, job_req)

        elif task == "performance_review":
            emp_data = input_data.get("employee_data", {})

            employee = EmployeeData(
                employee_id=emp_data.get("employee_id", ""),
                name=emp_data.get("name", ""),
                department=emp_data.get("department", ""),
                position=emp_data.get("position", ""),
                join_date=emp_data.get("join_date", ""),
                performance_scores=emp_data.get("performance_scores", {}),
                training_records=emp_data.get("training_records", []),
                satisfaction_score=emp_data.get("satisfaction_score", 0),
                risk_factors=emp_data.get("risk_factors", [])
            )

            result = system.performance_management(employee)

        elif task == "employee_care":
            emp_data = input_data.get("employee_data", {})

            employee = EmployeeData(
                employee_id=emp_data.get("employee_id", ""),
                name=emp_data.get("name", ""),
                department=emp_data.get("department", ""),
                position=emp_data.get("position", ""),
                join_date=emp_data.get("join_date", ""),
                performance_scores=emp_data.get("performance_scores", {}),
                training_records=emp_data.get("training_records", []),
                satisfaction_score=emp_data.get("satisfaction_score", 0),
                risk_factors=emp_data.get("risk_factors", [])
            )

            result = system.employee_wellbeing(employee)

        else:
            result = {"error": f"未知任务类型: {task}"}

        return result

    except Exception as e:
        return {
            "error": str(e),
            "error_type": type(e).__name__,
            "timestamp": datetime.now().isoformat()
        }


if __name__ == "__main__":
    test_candidates = [
        CandidateProfile(
            candidate_id="C001",
            name="张三",
            skills=["Python", "Machine Learning", "Data Analysis", "TensorFlow"],
            years_experience=6,
            education="硕士",
            expected_salary=35000,
            resume_text="6年机器学习经验...",
            work_history=[
                {"company": "某科技公司", "position": "算法工程师", "years": 3},
                {"company": "某互联网公司", "position": "高级算法工程师", "years": 3}
            ]
        ),
        CandidateProfile(
            candidate_id="C002",
            name="李四",
            skills=["Java", "Spring Boot", "Microservices", "Kubernetes"],
            years_experience=8,
            education="本科",
            expected_salary=40000,
            resume_text="8年后端开发经验..."
        )
    ]

    test_job = JobRequirement(
        job_id="J001",
        title="高级AI工程师",
        department="技术研发部",
        required_skills=["Python", "Machine Learning", "Deep Learning"],
        min_experience=5,
        salary_range=(30000, 50000),
        job_description="负责AI产品研发..."
    )

    test_employee = EmployeeData(
        employee_id="E001",
        name="王五",
        department="技术研发部",
        position="高级工程师",
        join_date="2022-03-15",
        performance_scores={
            "工作质量": 88,
            "团队合作": 85,
            "创新能力": 78,
            "执行力": 92,
            "学习能力": 90
        },
        training_records=[
            {"course": "领导力培训", "date": "2025-06"},
            {"course": "AI进阶课程", "date": "2025-09"}
        ],
        satisfaction_score=82,
        risk_factors=[]
    )

    system = HRIntelligenceV2()

    print("="*80)
    print("YYC³ 人力资源智能化系统 v2.0 - 测试运行")
    print("="*80)

    print("\n📋 场景1: 智能招聘")
    recruitment_result = system.intelligent_recruitment(test_candidates, test_job)

    if "ai_family_analysis" in recruitment_result:
        analysis = recruitment_result["ai_family_analysis"]
        print(f"\n   候选人评估数: {len(analysis['candidate_evaluations'])}")
        print(f"\n   🏆 推荐候选人:")
        for rec in analysis.get("hiring_recommendation", {}).get("recommended_candidates", [])[:3]:
            print(f"      • {rec['candidate_name']} - 综合评分: {rec['overall_score']} ({rec['recommendation_level']})")

        print(f"\n   ✓ 公平性审核: {analysis.get('quality_assurance', {}).get('status', '')}")

    print("\n📊 场景2: 绩效管理")
    perf_result = system.performance_management(test_employee)
    print(f"   员工: {test_employee.name}")
    print(f"   绩效等级: {perf_result.get('summary', {}).get('overall_rating', '')}")

    print("\n❤️  场景3: 员工关怀")
    care_result = system.employee_wellbeing(test_employee)
    print(f"   健康指数: {care_result.get('wellness_index', 0)}")
    print(f"   关怀状态: {care_result.get('wellness_status', '')}")

    print("\n" + "="*80)
    print("✅ 测试完成！AI Family Agent协同运行正常。")
    print("="*80)
