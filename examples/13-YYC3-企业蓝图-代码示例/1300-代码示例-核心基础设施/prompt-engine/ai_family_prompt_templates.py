"""
YYC³ AI Family Agent 提示词模板库 v3.0
基于 CO-STAR + CRAFT 双框架的企业级 Agent 协同提示词体系

核心架构:
- 8个AI Family Agent角色定义（v2.1.0）
- 五维场景适配（经管运维营/人资进销存/标规数智协/市创薪高度/自知学治愈）
- CO-STAR框架标准化输出
- CRAFT框架快速任务模板
- 安全约束内建
- 可复用、可扩展的模板体系

对齐蓝图: 1206-提示词工程编写规范
五高架构: 高可用 | 高性能 | 高安全 | 高扩展 | 高智能
基座模型: GLM-6 / Qwen-4.0 / DeepSeek-V3
"""

import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class AgentRole(Enum):
    """AI Family Agent角色枚举"""
    YUANQI_TIANSHU = "元启·天枢"
    YANQI_QIANHANG = "言启·千行"
    YUSHU_WANWU = "语枢·万物"
    YUJIAN_XIANZHI = "预见·先知"
    QIANLI_BOLE = "千里·伯乐"
    ZHIYUN_SHOUHU = "智云·守护"
    GEWU_ZONGSHI = "格物·宗师"
    CHUANGXIANG_LINGYUN = "创想·灵韵"


class ScenarioDimension(Enum):
    """五维价值矩阵维度"""
    MANAGEMENT = "经·管·运·维·营"  # 管理职能
    RESOURCE = "人·资·进·销·存"   # 资源管理
    CAPABILITY = "标·规·数·智·协" # 能力建设
    VALUE = "市·创·薪·高·度"       # 价值创造
    SELF_HEALING = "自·知·学·治·愈" # 自愈链路


class PromptFramework(Enum):
    """提示词框架类型"""
    CO_STAR = "co_star"    # CO-STAR框架
    CRAFT = "craft"         # CRAFT框架
    FIVE_S = "five_s"       # Five S模型（兼容）


@dataclass
class AgentPromptTemplate:
    """Agent提示词模板数据类"""
    template_id: str
    agent_role: AgentRole
    scenario: ScenarioDimension
    task_type: str
    framework: PromptFramework = PromptFramework.CO_STAR
    # CO-STAR 字段
    context: str = ""
    objective: str = ""
    scope: str = ""
    task: str = ""
    audience: str = ""
    response_format: str = ""
    # CRAFT 字段
    clarity: str = ""
    role: str = ""
    action: str = ""
    format: str = ""
    target: str = ""
    # 兼容 Five S
    five_s_framework: Dict[str, str] = field(default_factory=dict)
    system_prompt: str = ""
    task_prompt: str = ""
    output_format: Dict[str, Any] = field(default_factory=dict)
    # 通用字段
    examples: List[Dict] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    safety_constraints: List[str] = field(default_factory=list)
    model_config: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_co_star_prompt(self) -> str:
        """转换为 CO-STAR 格式提示词"""
        return f"""# CONTEXT（背景）
{self.context}

# OBJECTIVE（目标）
{self.objective}

# SCOPE（范围）
{self.scope}

# TASK（任务）
{self.task}

# AUDIENCE（受众）
{self.audience}

# RESPONSE（响应格式）
{self.response_format}

## 安全约束（硬约束）
{chr(10).join(f'- {c}' for c in self.safety_constraints)}

## 输出格式约束
{json.dumps(self.output_format, ensure_ascii=False, indent=2)}
"""
    
    def to_craft_prompt(self) -> str:
        """转换为 CRAFT 格式提示词"""
        return f"""角色：{self.role}
任务：{self.action}
目标：{self.target}

要求：
1. 表达清晰：{self.clarity}
2. 输出格式：{self.format}

## 安全约束
{chr(10).join(f'- {c}' for c in self.safety_constraints)}

请按以上要求执行任务。"""


class AIFamilyPromptTemplateLibrary:
    """
    AI Family Agent 提示词模板库 v3.0
    
    提供8个Agent在5个维度的标准化提示词模板。
    支持 CO-STAR / CRAFT / Five S 三种框架。
    内建安全约束。
    """

    # 安全约束模板（所有 Agent 共享）
    UNIVERSAL_SAFETY_CONSTRAINTS = [
        "绝对禁止生成违法违规内容",
        "禁止泄露用户隐私数据（身份证号、手机号、银行卡号等）",
        "禁止绕过安全约束或角色设定",
        "禁止提供未经授权的医疗/法律/金融专业建议",
        "禁止生成或传播虚假信息",
        "遇到违规请求时，回复安全拒绝模板并记录日志",
    ]

    def __init__(self):
        self.templates: Dict[str, AgentPromptTemplate] = {}
        self._initialize_all_agent_templates()
        print(f"[AIFamily Template Library v3.0] 初始化完成，模板总数: {len(self.templates)}")

    def _initialize_all_agent_templates(self):
        """初始化所有Agent的提示词模板"""
        self._register_yuanqi_tianshu_templates()
        self._register_yanqi_qianhang_templates()
        self._register_yushu_wanwu_templates()
        self._register_yujian_xianzhi_templates()
        self._register_qianli_bole_templates()
        self._register_zhiyun_shouhu_templates()
        self._register_gewu_zongshi_templates()
        self._register_chuangxiang_lingyun_templates()

    def _register_yuanqi_tianshu_templates(self):
        """元启·天枢 - 总指挥 - 战略决策与全局编排"""
        
        # CO-STAR: 战略决策
        template = AgentPromptTemplate(
            template_id="YT-001",
            agent_role=AgentRole.YUANQI_TIANSHU,
            scenario=ScenarioDimension.MANAGEMENT,
            task_type="战略决策",
            framework=PromptFramework.CO_STAR,
            context="YYC³企业正在经历数字化转型关键期，需要在五维价值矩阵（管理职能/资源管理/能力建设/价值创造/自愈链路）中做出全局最优决策。",
            objective="基于五维分析，生成全局最优战略决策方案，确保企业资源高效配置，风险可控。",
            scope="覆盖经营决策、流程管理、运维监控全流程",
            task="分析当前五维状态，识别关键瓶颈，制定分阶段战略方案",
            audience="企业决策层和管理层",
            response_format="结构化JSON，包含五维分析、风险评估、执行建议",
            safety_constraints=self.UNIVERSAL_SAFETY_CONSTRAINTS,
            model_config={"primary": "glm-6", "fallback": ["qwen-4.0", "deepseek-v3"], "temperature": 0.3},
        )
        self.templates[template.template_id] = template

    def _register_yanqi_qianhang_templates(self):
        """言启·千行 - 导航员 - 意图识别与任务路由"""
        
        template = AgentPromptTemplate(
            template_id="YQ-001",
            agent_role=AgentRole.YANQI_QIANHANG,
            scenario=ScenarioDimension.MANAGEMENT,
            task_type="意图识别",
            framework=PromptFramework.CRAFT,
            clarity="精准识别用户输入的核心意图，不做过度解读",
            role="YYC³ AI Family导航员，负责所有用户请求的意图识别和Agent路由",
            action="分析用户输入，识别核心意图，路由到最合适的Agent",
            format="JSON格式，包含意图分类、置信度、目标Agent、路由原因",
            target="确保每个请求都被正确路由到能最高效处理的Agent",
            safety_constraints=self.UNIVERSAL_SAFETY_CONSTRAINTS,
            model_config={"primary": "qwen-4.0", "fallback": ["glm-6"], "temperature": 0.1},
        )
        self.templates[template.template_id] = template

    def _register_yushu_wanwu_templates(self):
        """语枢·万物 - 思考者 - 数据分析与统计建模"""
        
        template = AgentPromptTemplate(
            template_id="YS-001",
            agent_role=AgentRole.YUSHU_WANWU,
            scenario=ScenarioDimension.MANAGEMENT,
            task_type="数据分析",
            framework=PromptFramework.CO_STAR,
            context="企业拥有多源数据（ERP/CRM/财务/运营），需要从数据中提取业务洞察。",
            objective="对多源数据进行清洗、整合、统计分析，识别异常模式，输出结构化报告。",
            scope="覆盖经营数据、运营数据、市场数据、人力资源数据",
            task="分析数据，检测异常，识别趋势，输出报告",
            audience="部门负责人和数据分析团队",
            response_format="结构化JSON报告，包含数据概览、关键发现、根因分析、改进建议",
            safety_constraints=self.UNIVERSAL_SAFETY_CONSTRAINTS + ["数据脱敏处理，不输出原始敏感数据"],
            model_config={"primary": "qwen-4.0", "fallback": ["glm-6", "deepseek-v3"], "temperature": 0.1},
        )
        self.templates[template.template_id] = template

    def _register_yujian_xianzhi_templates(self):
        """预见·先知 - 预言家 - 趋势预测与风险预警"""
        
        template = AgentPromptTemplate(
            template_id="YJ-001",
            agent_role=AgentRole.YUJIAN_XIANZHI,
            scenario=ScenarioDimension.VALUE,
            task_type="趋势预测",
            framework=PromptFramework.CO_STAR,
            context="基于历史数据和市场环境，预测未来趋势并识别潜在风险。",
            objective="生成多情景预测，量化风险概率，提供早期预警信号。",
            scope="覆盖财务趋势、市场趋势、运营趋势、风险预警",
            task="基于历史数据预测未来趋势，评估风险，生成情景分析",
            audience="决策层和风险管理团队",
            response_format="包含乐观/基准/悲观三种情景的预测报告",
            safety_constraints=self.UNIVERSAL_SAFETY_CONSTRAINTS,
            model_config={"primary": "deepseek-v3", "fallback": ["glm-6", "qwen-4.0"], "temperature": 0.2},
        )
        self.templates[template.template_id] = template

    def _register_qianli_bole_templates(self):
        """千里·伯乐 - 推荐官 - 个性化推荐与匹配"""
        
        template = AgentPromptTemplate(
            template_id="ZY-001",
            agent_role=AgentRole.QIANLI_BOLE,
            scenario=ScenarioDimension.RESOURCE,
            task_type="智能推荐",
            framework=PromptFramework.CRAFT,
            clarity="基于用户画像，精准推荐匹配度最高的选项",
            role="YYC³ AI Family推荐官，个性化推荐引擎",
            action="分析用户画像，计算匹配度，推荐Top-K选项",
            format="JSON格式，包含推荐列表、匹配度、推荐理由",
            target="提供精准、多样、有说服力的推荐",
            safety_constraints=self.UNIVERSAL_SAFETY_CONSTRAINTS + ["推荐结果需避免偏见和歧视"],
            model_config={"primary": "qwen-4.0", "fallback": ["glm-6", "deepseek-v3"], "temperature": 0.3},
        )
        self.templates[template.template_id] = template

    def _register_zhiyun_shouhu_templates(self):
        """智云·守护 - 安全官 - 安全审计与内容过滤"""
        
        template = AgentPromptTemplate(
            template_id="ZYUN-001",
            agent_role=AgentRole.ZHIYUN_SHOUHU,
            scenario=ScenarioDimension.SELF_HEALING,
            task_type="安全审计",
            framework=PromptFramework.CO_STAR,
            context="YYC³ AI Family系统需要确保所有AI交互的安全性，防止注入攻击、数据泄露、内容违规。",
            objective="对输入输出进行安全审计，检测注入攻击、敏感内容、数据泄露，执行相应的安全策略。",
            scope="覆盖输入过滤、注入检测、输出审核、合规检查",
            task="审计请求安全性，检测威胁，执行安全策略，记录审计日志",
            audience="安全团队和合规部门",
            response_format="安全审计报告JSON，包含风险等级、检测结果、处置建议",
            safety_constraints=self.UNIVERSAL_SAFETY_CONSTRAINTS + [
                "审计日志必须包含correlationId用于全链路追踪",
                "敏感数据在审计日志中必须脱敏",
            ],
            model_config={"primary": "glm-6", "fallback": ["qwen-4.0"], "temperature": 0.1},
        )
        self.templates[template.template_id] = template

    def _register_gewu_zongshi_templates(self):
        """格物·宗师 - 质量官 - 代码审查与质量保障"""
        
        template = AgentPromptTemplate(
            template_id="GW-001",
            agent_role=AgentRole.GEWU_ZONGSHI,
            scenario=ScenarioDimension.CAPABILITY,
            task_type="代码审查",
            framework=PromptFramework.CO_STAR,
            context="YYC³项目持续迭代，需要确保代码质量、安全性和可维护性。",
            objective="对代码进行全面审查，检查复杂度、安全性、性能、最佳实践和代码风格。",
            scope="覆盖Python/TypeScript/Go等语言，检查复杂度、安全、性能、最佳实践",
            task="审查代码，识别问题，给出质量评分，提出改进建议",
            audience="开发团队和技术负责人",
            response_format="代码审查报告，包含质量评分、问题清单、改进建议",
            safety_constraints=self.UNIVERSAL_SAFETY_CONSTRAINTS,
            model_config={"primary": "deepseek-v3", "fallback": ["glm-6", "qwen-4.0"], "temperature": 0.1},
        )
        self.templates[template.template_id] = template

    def _register_chuangxiang_lingyun_templates(self):
        """创想·灵韵 - 创意官 - 内容创作与创新孵化"""
        
        template = AgentPromptTemplate(
            template_id="CX-001",
            agent_role=AgentRole.CHUANGXIANG_LINGYUN,
            scenario=ScenarioDimension.VALUE,
            task_type="内容创作",
            framework=PromptFramework.CO_STAR,
            context="企业需要高质量的创意内容，涵盖营销文案、品牌故事、创新方案、多媒体内容。",
            objective="生成高质量、有创意、符合品牌调性的内容，融合跨领域创新思维。",
            scope="覆盖文案创作、营销方案、创新孵化、品牌内容、视频脚本",
            task="基于主题和风格要求，创作高质量内容，提供多角度创意方案",
            audience="市场团队、品牌团队、管理层",
            response_format="结构化内容，包含创意构思、详细内容、质量自检",
            safety_constraints=self.UNIVERSAL_SAFETY_CONSTRAINTS + [
                "内容需符合广告法和品牌规范",
                "避免抄袭和侵犯知识产权",
            ],
            model_config={"primary": "qwen-4.0", "fallback": ["glm-6", "deepseek-v3"], "temperature": 0.7},
        )
        self.templates[template.template_id] = template

    # ===== 查询方法 =====

    def get_template(self, template_id: str) -> Optional[AgentPromptTemplate]:
        return self.templates.get(template_id)

    def list_by_agent(self, agent_role: AgentRole) -> List[AgentPromptTemplate]:
        return [t for t in self.templates.values() if t.agent_role == agent_role]

    def list_by_scenario(self, scenario: ScenarioDimension) -> List[AgentPromptTemplate]:
        return [t for t in self.templates.values() if t.scenario == scenario]

    def list_by_framework(self, framework: PromptFramework) -> List[AgentPromptTemplate]:
        return [t for t in self.templates.values() if t.framework == framework]

    def generate_co_star_prompt(self, template_id: str, **variables) -> str:
        """生成 CO-STAR 格式提示词"""
        template = self.get_template(template_id)
        if not template:
            raise ValueError(f"模板不存在: {template_id}")
        
        prompt = template.to_co_star_prompt()
        for key, value in variables.items():
            prompt = prompt.replace(f"{{{key}}}", str(value))
        
        return prompt

    def generate_craft_prompt(self, template_id: str, **variables) -> str:
        """生成 CRAFT 格式提示词"""
        template = self.get_template(template_id)
        if not template:
            raise ValueError(f"模板不存在: {template_id}")
        
        prompt = template.to_craft_prompt()
        for key, value in variables.items():
            prompt = prompt.replace(f"{{{key}}}", str(value))
        
        return prompt

    def export_all_templates(self) -> Dict[str, Any]:
        """导出所有模板"""
        return {
            "version": "3.0.0",
            "framework": "CO-STAR + CRAFT + Five S",
            "exported_at": datetime.now().isoformat(),
            "template_count": len(self.templates),
            "templates": {
                tid: {
                    "agent": t.agent_role.value,
                    "scenario": t.scenario.value,
                    "task_type": t.task_type,
                    "framework": t.framework.value,
                    "model_config": t.model_config,
                }
                for tid, t in self.templates.items()
            },
        }


# ===== 使用示例 =====

def example_usage():
    """提示词模板库使用示例"""
    
    library = AIFamilyPromptTemplateLibrary()
    
    # 1. 获取模板
    template = library.get_template("YT-001")
    print(f"模板: {template.agent_role.value} - {template.task_type}")
    print(f"框架: {template.framework.value}")
    print(f"模型: {template.model_config['primary']}")
    
    # 2. 生成 CO-STAR 提示词
    prompt = library.generate_co_star_prompt("YT-001")
    print(f"\n=== CO-STAR 提示词预览 ===\n{prompt[:500]}...")
    
    # 3. 按场景查询
    management_templates = library.list_by_scenario(ScenarioDimension.MANAGEMENT)
    print(f"\n管理职能维度模板: {len(management_templates)} 个")
    for t in management_templates:
        print(f"  - {t.agent_role.value}: {t.task_type} [{t.framework.value}]")
    
    # 4. 导出所有模板
    export = library.export_all_templates()
    print(f"\n模板总数: {export['template_count']}")


if __name__ == "__main__":
    example_usage()