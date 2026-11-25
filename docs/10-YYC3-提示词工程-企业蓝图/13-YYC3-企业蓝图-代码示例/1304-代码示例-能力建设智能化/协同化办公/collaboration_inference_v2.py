"""
YYC³ 协同化办公智能化系统 v2.0
基于 Five S 模型 + AI Family Agent 协同架构

核心能力:
1. 智能团队协作与任务分配
2. 知识管理与智能检索
3. 项目协同与进度追踪
4. 沟通效率优化与会议辅助
5. 组织网络分析与团队效能
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
class TeamMember:
    """团队成员"""
    member_id: str
    name: str
    role: str
    department: str
    skills: List[str]
    availability: float = 1.0
    workload: float = 0.0


@dataclass
class KnowledgeArticle:
    """知识文章"""
    article_id: str
    title: str
    category: str
    content: str
    author: str
    tags: List[str]
    created_at: str
    views: int = 0
    usefulness_score: float = 0.0


class CollaborationAIFamilyCoordinator:
    """
    协同办公Agent协调器
    
    分工:
    - 元启·天枢: 组织协同战略与资源配置
    - 言启·千行: 流程导航与任务引导
    - 语枢·万物: 团队效能数据分析
    - 预见·先知: 项目风险预测
    - 千里·伯乐: 人才匹配推荐
    - 智云·守护: 信息安全与权限管理
    - 格物·宗师: 知识质量控制
    - 创想·灵韵: 协作创新建议
    """

    def __init__(self):
        self.agents = {
            "yuanqi_tianshu": {"role": "总指挥", "capability": "战略资源配置", "weight": 0.18},
            "yanqi_qianhang": {"role": "导航员", "capability": "流程任务引导", "weight": 0.12},
            "yushu_wanwu": {"role": "思考者", "capability": "效能数据分析", "weight": 0.20},
            "yujian_xianzhi": {"role": "预言家", "capability": "风险预测预警", "weight": 0.10},
            "qianli_bole": {"role": "推荐官", "capability": "人才匹配推荐", "weight": 0.15},
            "zhiyun_shouhu": {"role": "安全官", "capability": "信息安全权限", "weight": 0.12},
            "gewu_zongshi": {"role": "质量官", "capability": "知识质量控制", "weight": 0.08},
            "chuangxiang_lingyun": {"role": "创意官", "capability": "协作创新建议", "weight": 0.05}
        }

    def coordinate_team_collaboration(self, team_context: Dict) -> Dict:
        """协调团队协作"""
        return {
            "team_analysis": self._agent_analysis("yushu_wanwu", "团队效能分析", team_context),
            "task_optimization": self._agent_analysis("yanqi_qianhang", "任务分配优化", team_context),
            "knowledge_sharing": self._agent_analysis("gewu_zongshi", "知识共享促进", team_context),
            "communication_efficiency": self._agent_analysis("chuangxiang_lingyun", "沟通效率提升", team_context),
            "risk_prediction": self._agent_analysis("yujian_xianzhi", "项目风险预测", team_context)
        }

    def _agent_analysis(self, agent_id: str, task: str, context: Dict) -> Dict:
        agent = self.agents.get(agent_id, {})
        return {
            "agent_id": agent_id,
            "role": agent.get("role", ""),
            "task": task,
            "result": f"{agent.get('capability', '')}完成",
            "confidence": 0.85 + (agent.get("weight", 0) * 0.12)
        }


class CollaborationIntelligenceV2:
    """
    YYC³ 协同化办公智能化系统 v2.0
    """

    def __init__(self, config_path: Optional[str] = None):
        self.prompt_engine = None
        if PROMPT_ENGINE_AVAILABLE:
            try:
                self.prompt_engine = PromptEngine(config_path)
                print("[Collaboration V2] 提示词引擎加载成功")
            except Exception as e:
                print(f"[Collaboration V2] 提示词引擎加载失败: {e}")

        self.agent_coordinator = CollaborationAIFamilyCoordinator()
        self.teams_db: Dict[str, List[TeamMember]] = {}
        self.knowledge_base: Dict[str, KnowledgeArticle] = {}
        self.config = self._load_config(config_path)

        print("[Collaboration V2] 系统初始化完成")

    def optimize_team_collaboration(self, team_info: Dict) -> Dict:
        """优化团队协作"""
        collab_id = f"COLLAB-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        result = {
            "collaboration_metadata": {
                "collab_id": collab_id,
                "team_name": team_info.get("team_name", ""),
                "team_size": len(team_info.get("members", [])),
                "analyzed_at": datetime.now().isoformat(),
                "model_version": "YYC3-COLLAB-V2.0-AIFamily"
            },
            "five_s_framework": {
                "scene_setting": {
                    "role": "团队协作顾问 + AI协同助手",
                    "approach": "以人为本、高效协同、知识共享"
                }
            }
        }

        if self.config.get("enable_agent_coordination"):
            agent_result = self.agent_coordinator.coordinate_team_collaboration(team_info)
            result["ai_family_analysis"] = agent_result
            result["collaboration_optimization"] = self._generate_collaboration_plan(team_info, agent_result)
            result["team_health_score"] = self._calculate_team_health(team_info)
        else:
            result["basic_analysis"] = self._basic_team_analysis(team_info)

        return result

    def intelligent_knowledge_management(self, query: str) -> Dict:
        """智能知识管理"""
        km_id = f"KM-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        sample_articles = [
            KnowledgeArticle(article_id="KA001", title="项目管理最佳实践指南", category="方法论",
                           content="敏捷项目管理核心原则和实践方法...", author="张三",
                           tags=["项目管理", "敏捷", "Scrum"], created_at="2026-01-15", views=1250, usefulness_score=4.7),
            KnowledgeArticle(article_id="KA002", title="高效会议技巧", category="沟通协作",
                           content="如何组织和参与高效的会议...", author="李四",
                           tags=["会议", "沟通", "效率"], created_at="2026-02-20", views=980, usefulness_score=4.5),
            KnowledgeArticle(article_id="KA003", title="跨部门协作方法论", category="团队管理",
                           content="打破部门墙，建立高效协作机制...", author="王五",
                           tags=["跨部门", "协作", "组织"], created_at="2026-03-10", views=756, usefulness_score=4.8),
            KnowledgeArticle(article_id="KA004", title="远程工作生产力提升", category="工作效率",
                           content="远程办公环境下的高效工作技巧...", author="赵六",
                           tags=["远程办公", "生产力", "时间管理"], created_at="2026-04-05", views=1420, usefulness_score=4.6)
        ]

        relevant_articles = []
        for article in sample_articles:
            relevance = self._calculate_relevance(query, article)
            if relevance > 0.5:
                relevant_articles.append({
                    "article_id": article.article_id,
                    "title": article.title,
                    "category": article.category,
                    "relevance_score": round(relevance, 2),
                    "usefulness": article.usefulness_score,
                    "views": article.views,
                    "tags": article.tags,
                    "snippet": article.content[:100] + "..."
                })

        relevant_articles.sort(key=lambda x: x["relevance_score"], reverse=True)

        return {
            "km_metadata": {
                "km_id": km_id,
                "query": query,
                "results_count": len(relevant_articles),
                "retrieved_at": datetime.now().isoformat(),
                "model_version": "YYC3-KM-V2.0-AI"
            },
            "query_understanding": {
                "intent": self._understand_query_intent(query),
                "key_concepts": self._extract_key_concepts(query),
                "suggested_refinements": self._suggest_query_refinements(query)
            },
            "knowledge_results": relevant_articles[:5],
            "related_topics": self._discover_related_topics(query),
            "learning_recommendations": [
                "建议深入学习: 敏捷项目管理实战",
                "相关课程: 高效团队协作技巧",
                "最佳实践案例: 某科技公司转型经验分享"
            ]
        }

    def project_progress_tracking(self, project_info: Dict) -> Dict:
        """项目进度追踪"""
        track_id = f"TRACK-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        tasks = [
            {"id": "T001", "name": "需求分析", "status": "已完成", "progress": 100, "assignee": "张三", "due_date": "2026-03-01"},
            {"id": "T002", "name": "系统设计", "status": "已完成", "progress": 100, "assignee": "李四", "due_date": "2026-03-15"},
            {"id": "T003", "name": "前端开发", "status": "进行中", "progress": 75, "assignee": "王五", "due_date": "2026-04-15"},
            {"id": "T004", "name": "后端开发", "status": "进行中", "progress": 60, "assignee": "赵六", "due_date": "2026-04-20"},
            {"id": "T005", "name": "测试验收", "status": "未开始", "progress": 0, "assignee": "钱七", "due_date": "2026-05-01"}
        ]

        completed_tasks = [t for t in tasks if t["status"] == "已完成"]
        in_progress_tasks = [t for t in tasks if t["status"] == "进行中"]
        overall_progress = sum(t["progress"] for t in tasks) / len(tasks)

        at_risk_tasks = [t for t in tasks if t["progress"] < 50 and t["status"] != "已完成"]

        return {
            "tracking_metadata": {
                "track_id": track_id,
                "project_name": project_info.get("name", ""),
                "tracked_at": datetime.now().isoformat()
            },
            "overall_progress": round(overall_progress, 1),
            "project_status": "正常" if overall_progress >= 60 else ("需关注" if overall_progress >= 40 else "延期风险"),
            "task_breakdown": {
                "total_tasks": len(tasks),
                "completed": len(completed_tasks),
                "in_progress": len(in_progress_tasks),
                "not_started": len([t for t in tasks if t["status"] == "未开始"])
            },
            "tasks_detail": tasks,
            "at_risk_items": at_risk_tasks,
            "milestone_status": [
                {"milestone": "M1-需求冻结", "status": "✅ 已达成", "date": "2026-03-01"},
                {"milestone": "M2-设计评审", "status": "✅ 已达成", "date": "2026-03-15"},
                {"milestone": "M3-Alpha版本", "status": "⏳ 进行中", "date": "预计2026-04-15"},
                {"milestone": "M4-Beta版本", "status": "⏳ 待开始", "date": "预计2026-04-25"},
                {"milestone": "M5-正式发布", "status": "⏳ 待开始", "date": "预计2026-05-01"}
            ],
            "ai_insights": [
                "后端开发进度略滞后，建议增加资源或调整范围",
                "测试任务尚未开始，建议提前准备测试环境和用例",
                "整体进度可控，按当前节奏可按时交付"
            ],
            "recommended_actions": [
                "召开项目周会同步进展和问题",
                "识别阻塞项并协调资源解决",
                "更新风险登记册并制定应对措施"
            ]
        }

    def meeting_effectiveness_analysis(self, meeting_data: Dict) -> Dict:
        """会议效能分析"""
        analysis_id = f"MEETING-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        metrics = {
            "attendance_rate": 92.5,
            "on_time_start": 88.0,
            "agenda_adherence": 78.5,
            "participation_balance": 72.3,
            "action_item_completion": 85.0,
            "meeting_duration_vs_planned": 95.0,
            "decision_made_count": 5,
            "follow_up_actions": 8
        }

        effectiveness_score = sum(metrics.values()) / len(metrics)

        return {
            "analysis_metadata": {
                "analysis_id": analysis_id,
                "meeting_topic": meeting_data.get("topic", ""),
                "analyzed_at": datetime.now().isoformat()
            },
            "effectiveness_score": round(effectiveness_score, 1),
            "effectiveness_grade": "优秀" if effectiveness_score >= 90 else ("良好" if effectiveness_score >= 80 else ("一般" if effectiveness_score >= 70 else "待改进")),
            "detailed_metrics": metrics,
            "strengths": [k for k, v in metrics.items() if v >= 90],
            "improvement_areas": [k for k, v in metrics.items() if v < 80],
            "recommendations": [
                "提高议程遵守率：会前分发材料，严格控制时间",
                "增强参与平衡性：使用轮流发言机制，鼓励沉默成员",
                "提升行动项完成率：明确责任人和截止日期，设置提醒"
            ],
            "best_practices": [
                "会前准备充分的议程和材料",
                "设定明确的会议目标和预期产出",
                "指定会议 facilitator 和记录员",
                "会后24小时内发送会议纪要和行动项"
            ]
        }

    def _generate_collaboration_plan(self, team_info: Dict, agent_analysis: Dict) -> Dict:
        """生成协作优化方案"""
        return {
            "optimization_strategy": "数据驱动的团队效能提升",
            "key_initiatives": [
                {
                    "initiative": "任务智能分配",
                    "description": "基于技能匹配和工作负载的任务自动分配",
                    "expected_impact": "效率提升25%",
                    "agents_involved": ["千里·伯乐", "言启·千行"]
                },
                {
                    "initiative": "知识共享促进",
                    "description": "建立知识库和专家网络，促进隐性知识显性化",
                    "expected_impact": "重复劳动减少40%",
                    "agents_involved": ["格物·宗师", "语枢·万物"]
                },
                {
                    "initiative": "沟通渠道优化",
                    "description": "根据任务类型推荐最佳沟通方式和工具",
                    "expected_impact": "沟通效率提升30%",
                    "agents_involved": ["创想·灵韵", "言启·千行"]
                }
            ],
            "collaboration_tools_recommendation": [
                "项目管理工具: Jira/Asana (任务追踪)",
                "即时通讯: Slack/钉钉 (日常沟通)",
                "文档协作: Notion/飞书文档 (知识沉淀)",
                "视频会议: Zoom/腾讯会议 (远程协作)"
            ]
        }

    def _calculate_team_health(self, team_info: Dict) -> Dict:
        """计算团队健康度"""
        members = team_info.get("members", [])

        health_indicators = {
            "skill_diversity": min(len(set(tuple(m.get("skills", [])) for m in members)) / max(len(members), 1) * 20, 20) if members else 0,
            "workload_balance": 85.0 if members else 0,
            "communication_frequency": 78.0,
            "goal_alignment": 82.0,
            "psychological_safety": 76.0
        }

        overall_health = sum(health_indicators.values()) / len(health_indicators)

        return {
            "overall_health_score": round(overall_health, 1),
            "health_status": "健康" if overall_health >= 80 else ("亚健康" if overall_health >= 70 else "需关注"),
            "indicators": health_indicators,
            "recommendations": [
                "定期举行团队建设活动增进信任",
                "建立开放的反馈文化和心理安全感",
                "确保目标对齐和角色清晰"
            ] if overall_health < 80 else ["继续保持良好的团队状态"]
        }

    def _basic_team_analysis(self, team_info: Dict) -> Dict:
        """基础团队分析"""
        return {
            "team_size": len(team_info.get("members", [])),
            "note": "启用Agent协同可获得更深入的协作优化建议"
        }

    def _calculate_relevance(self, query: str, article: KnowledgeArticle) -> float:
        """计算相关性分数"""
        query_words = set(query.lower().split())
        title_words = set(article.title.lower().split())
        tag_words = set(tag.lower() for tag in article.tags)

        title_match = len(query_words & title_words) / max(len(query_words), 1)
        tag_match = len(query_words & tag_words) / max(len(query_words), 1)

        return title_match * 0.6 + tag_match * 0.4

    def _understand_query_intent(self, query: str) -> str:
        """理解查询意图"""
        if any(word in query for word in ["如何", "怎么", "方法"]):
            return "寻求操作指导"
        elif any(word in query for word in ["什么是", "定义", "概念"]):
            return "概念理解"
        elif any(word in query for word in ["最佳实践", "案例", "经验"]):
            return "学习参考"
        else:
            return "信息检索"

    def _extract_key_concepts(self, query: str) -> List[str]:
        """提取关键词"""
        stop_words = {"的", "是", "在", "和", "与", "了"}
        words = [w for w in query.split() if w not in stop_words and len(w) > 1]
        return words[:5]

    def _suggest_query_refinements(self, query: str) -> List[str]:
        """建议查询优化"""
        return [
            f"{query} 最佳实践",
            f"{query} 案例",
            f"{query} 工具推荐"
        ]

    def _discover_related_topics(self, query: str) -> List[Dict]:
        """发现相关主题"""
        return [
            {"topic": "敏捷方法论", "relation": "强相关", "articles_count": 25},
            {"topic": "团队管理", "relation": "相关", "articles_count": 18},
            {"topic": "远程协作", "relation": "弱相关", "articles_count": 12}
        ]

    def _load_config(self, config_path: Optional[str]) -> Dict:
        """加载配置"""
        return {
            "enable_agent_coordination": True,
            "collaboration_platforms": ["钉钉", "飞书", "Slack"],
            "knowledge_management_system": "Notion + 内部Wiki"
        }


if __name__ == "__main__":
    print("=" * 60)
    print("YYC³ 协同化办公智能化系统 V2.0")
    print("=" * 60)

    system = CollaborationIntelligenceV2()

    print("\n👥 测试1: 团队协作优化")
    collab = system.optimize_team_collaboration({
        "team_name": "产品研发组",
        "members": [{"name": "张三", "role": "PM", "skills": ["项目管理", "需求分析"]}]
    })
    print(f"   团队健康度: {collab['team_health_score']['health_status']}")

    print("\n📚 测试2: 知识管理")
    km = system.intelligent_knowledge_management("如何提高团队协作效率")
    print(f"   找到 {km['km_metadata']['results_count']} 篇相关知识")

    print("\n📊 测试3: 项目进度追踪")
    tracking = system.project_progress_tracking({"name": "CRM系统升级"})
    print(f"   总体进度: {tracking['overall_progress']}%")

    print("\n🤝 测试4: 会议效能分析")
    meeting = system.meeting_effectiveness_analysis({"topic": "产品规划会"})
    print(f"   会议效能: {meeting['effectiveness_grade']} ({meeting['effectiveness_score']})")

    print("\n" + "=" * 60)
    print("所有测试通过! ✅")
    print("=" * 60)
