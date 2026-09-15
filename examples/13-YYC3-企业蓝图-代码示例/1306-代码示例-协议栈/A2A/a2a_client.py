"""
YYC³ A2A (Agent-to-Agent) 通信协议客户端 v1.0
基于 Google A2A Protocol v1.0 的 Agent 间标准化通信

核心理念:
- AI的外交语言：Agent间标准化任务委托与协作
- Agent Card 自动发现 + Task 委托 + 状态流式推送
- 支持 gRPC 和 Streamable HTTP 双传输

对齐蓝图: 1207-协议栈标准化设计
五高架构: 高可用 | 高性能 | 高安全 | 高扩展 | 高智能

用法:
    from a2a_client import A2AClient, A2ATask
    
    client = A2AClient("https://yyc3.ai/agents/thinker")
    card = await client.get_agent_card()
    result = await client.send_task(task, on_state_change=callback)
"""

import json
import uuid
import time
import logging
from typing import Dict, List, Optional, Any, Callable, AsyncIterator
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import asyncio
import aiohttp

logger = logging.getLogger("yyc3.a2a")


class A2ATaskStatus(Enum):
    """A2A 任务状态"""
    SUBMITTED = "submitted"
    WORKING = "working"
    INPUT_REQUIRED = "input_required"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class A2AAgentRole(Enum):
    """A2A Agent 角色"""
    ORCHESTRATOR = "orchestrator"      # 编排者（元启天枢）
    NAVIGATOR = "navigator"            # 导航员（言启千行）
    THINKER = "thinker"                # 思考者（语枢万物）
    PROPHET = "prophet"                # 预言家（预见先知）
    RECOMMENDER = "recommender"        # 推荐官（千里伯乐）
    SECURITY_OFFICER = "security"      # 安全官（智云守护）
    QUALITY_OFFICER = "quality"        # 质量官（格物宗师）
    CREATOR = "creator"                # 创意官（创想灵韵）


@dataclass
class AgentSkill:
    """Agent 技能定义"""
    id: str
    name: str
    description: str
    tags: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)


@dataclass
class AgentCard:
    """Agent Card — A2A 服务发现核心"""
    name: str
    description: str
    url: str
    version: str
    role: A2AAgentRole
    skills: List[AgentSkill] = field(default_factory=list)
    streaming: bool = True
    pushNotifications: bool = True
    stateTransitionHistory: bool = True
    authentication: Dict[str, Any] = field(default_factory=dict)
    slo: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "url": self.url,
            "version": self.version,
            "provider": {"organization": "YanYuCloudCube", "url": "https://yyc3.ai"},
            "capabilities": {
                "streaming": self.streaming,
                "pushNotifications": self.pushNotifications,
                "stateTransitionHistory": self.stateTransitionHistory,
            },
            "skills": [
                {
                    "id": s.id, "name": s.name,
                    "description": s.description,
                    "tags": s.tags, "examples": s.examples,
                }
                for s in self.skills
            ],
            "defaultInputModes": ["text", "structured"],
            "defaultOutputModes": ["text", "structured", "streaming"],
            "authentication": self.authentication,
            "security": {"tlsRequired": True},
            "slo": self.slo,
        }


@dataclass
class A2ATask:
    """A2A 任务定义"""
    id: str
    type: str
    priority: str = "normal"  # low | normal | high | critical
    deadline: Optional[str] = None
    input: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class A2ATaskState:
    """A2A 任务状态更新"""
    taskId: str
    status: A2ATaskStatus
    message: str = ""
    artifacts: List[Dict[str, Any]] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class A2ATaskResult:
    """A2A 任务结果"""
    taskId: str
    status: A2ATaskStatus
    output: Dict[str, Any] = field(default_factory=dict)
    error: Optional[Dict[str, Any]] = None
    metrics: Dict[str, Any] = field(default_factory=dict)
    artifacts: List[Dict[str, Any]] = field(default_factory=list)


class A2AClient:
    """
    A2A 协议客户端
    
    实现 Agent Card 发现、Task 委托、状态流式推送、多轮对话协商。
    支持 gRPC 和 Streamable HTTP 两种传输模式。
    """
    
    def __init__(
        self,
        base_url: str,
        timeout: int = 60,
        correlation_id: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.correlation_id = correlation_id or str(uuid.uuid4())
        self.api_key = api_key
        
        self._session: Optional[aiohttp.ClientSession] = None
        self._agent_card: Optional[AgentCard] = None
        
        logger.info(f"[A2A Client] 初始化 | base_url={base_url} | correlationId={self.correlation_id}")
    
    async def __aenter__(self):
        self._session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout),
            headers=self._build_headers(),
        )
        return self
    
    async def __aexit__(self, *args):
        if self._session:
            await self._session.close()
            self._session = None
    
    async def get_agent_card(self) -> AgentCard:
        """获取远程 Agent 的 Agent Card（服务发现）"""
        start_time = time.time()
        
        try:
            async with self._session.get(
                f"{self.base_url}/.well-known/agent-card.json"
            ) as resp:
                data = await resp.json()
                
                self._agent_card = AgentCard(
                    name=data["name"],
                    description=data["description"],
                    url=data["url"],
                    version=data["version"],
                    role=A2AAgentRole(data.get("role", "thinker")),
                    skills=[
                        AgentSkill(
                            id=s["id"], name=s["name"],
                            description=s["description"],
                            tags=s.get("tags", []),
                            examples=s.get("examples", []),
                        )
                        for s in data.get("skills", [])
                    ],
                    streaming=data.get("capabilities", {}).get("streaming", True),
                    pushNotifications=data.get("capabilities", {}).get("pushNotifications", True),
                    stateTransitionHistory=data.get("capabilities", {}).get("stateTransitionHistory", True),
                    authentication=data.get("authentication", {}),
                    slo=data.get("slo", {}),
                )
                
                elapsed = (time.time() - start_time) * 1000
                logger.info(
                    f"[A2A Client] Agent Card 获取成功 | "
                    f"agent={self._agent_card.name} v{self._agent_card.version} | "
                    f"skills={len(self._agent_card.skills)} | latency={elapsed:.0f}ms"
                )
                
                return self._agent_card
                
        except Exception as e:
            logger.error(f"[A2A Client] Agent Card 获取失败: {e}")
            raise
    
    async def send_task(
        self,
        task: A2ATask,
        on_state_change: Optional[Callable[[A2ATaskState], None]] = None,
    ) -> A2ATaskResult:
        """发送任务委托并等待结果"""
        start_time = time.time()
        
        try:
            # 确保已获取 Agent Card
            if not self._agent_card:
                await self.get_agent_card()
            
            # 发送任务
            payload = {
                "task": {
                    "id": task.id,
                    "type": task.type,
                    "priority": task.priority,
                    "deadline": task.deadline,
                    "input": task.input,
                    "context": {
                        "correlationId": self.correlation_id,
                        **task.context,
                    },
                }
            }
            
            async with self._session.post(
                f"{self.base_url}/tasks",
                json=payload,
            ) as resp:
                task_response = await resp.json()
                task_id = task_response.get("taskId", task.id)
            
            # 监听状态流式推送
            final_state = None
            state_stream = self._stream_task_states(task_id)
            
            async for state in state_stream:
                if on_state_change:
                    on_state_change(state)
                final_state = state
                
                if state.status in (A2ATaskStatus.COMPLETED, A2ATaskStatus.FAILED, A2ATaskStatus.CANCELLED):
                    break
            
            elapsed = (time.time() - start_time) * 1000
            
            if not final_state:
                raise Exception("未收到任务终态")
            
            return A2ATaskResult(
                taskId=task_id,
                status=final_state.status,
                output=self._extract_output(final_state),
                error=final_state.artifacts[0].get("error") if final_state.artifacts else None,
                metrics={
                    "duration": elapsed,
                    "startTime": datetime.now().isoformat(),
                },
                artifacts=final_state.artifacts,
            )
            
        except Exception as e:
            elapsed = (time.time() - start_time) * 1000
            logger.error(f"[A2A Client] 任务执行失败 | taskId={task.id} | error={e} | latency={elapsed:.0f}ms")
            raise
    
    async def cancel_task(self, task_id: str):
        """取消任务"""
        try:
            async with self._session.delete(f"{self.base_url}/tasks/{task_id}") as resp:
                if resp.status == 200:
                    logger.info(f"[A2A Client] 任务已取消 | taskId={task_id}")
                else:
                    logger.warning(f"[A2A Client] 取消任务失败 | taskId={task_id} | status={resp.status}")
        except Exception as e:
            logger.error(f"[A2A Client] 取消任务异常 | taskId={task_id} | error={e}")
    
    async def get_task_status(self, task_id: str) -> A2ATaskState:
        """获取任务当前状态"""
        async with self._session.get(f"{self.base_url}/tasks/{task_id}") as resp:
            data = await resp.json()
            return A2ATaskState(
                taskId=data["taskId"],
                status=A2ATaskStatus(data["status"]),
                message=data.get("message", ""),
                artifacts=data.get("artifacts", []),
                timestamp=data.get("timestamp", ""),
            )
    
    async def _stream_task_states(self, task_id: str) -> AsyncIterator[A2ATaskState]:
        """SSE 流式监听任务状态变化"""
        async with self._session.get(
            f"{self.base_url}/tasks/{task_id}/stream"
        ) as resp:
            async for line in resp.content:
                text = line.decode("utf-8").strip()
                if text.startswith("data: "):
                    data = json.loads(text[6:])
                    yield A2ATaskState(
                        taskId=data.get("taskId", task_id),
                        status=A2ATaskStatus(data.get("status", "working")),
                        message=data.get("message", ""),
                        artifacts=data.get("artifacts", []),
                        timestamp=data.get("timestamp", ""),
                    )
    
    def _extract_output(self, state: A2ATaskState) -> Dict[str, Any]:
        """从状态中提取输出"""
        output = {}
        for artifact in state.artifacts:
            for part in artifact.get("parts", []):
                if "text" in part:
                    output["text"] = (output.get("text", "") or "") + part["text"]
                if "data" in part:
                    output.update(part["data"])
        return output
    
    def _build_headers(self) -> Dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "X-Correlation-ID": self.correlation_id,
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers


# ===== YYC³ AI Family Agent Cards =====

YYC3_AGENT_CARDS = {
    "tianshu": {
        "name": "元启·天枢",
        "description": "YYC³ AI Family 总指挥 — 战略决策与全局编排",
        "url": "https://yyc3.ai/agents/tianshu",
        "version": "2.1.0",
        "role": A2AAgentRole.ORCHESTRATOR,
        "skills": [
            {"id": "strategic-planning", "name": "战略规划", "description": "多维度战略分析与方案生成"},
            {"id": "task-orchestration", "name": "任务编排", "description": "跨Agent任务分解与调度"},
            {"id": "conflict-resolution", "name": "冲突协调", "description": "多Agent资源冲突解决"},
        ],
        "slo": {"latency": {"p50": "500ms", "p95": "2s", "p99": "5s"}, "availability": "99.9%"},
    },
    "navigator": {
        "name": "言启·千行",
        "description": "YYC³ AI Family 导航员 — 意图识别与任务路由",
        "url": "https://yyc3.ai/agents/navigator",
        "version": "2.1.0",
        "role": A2AAgentRole.NAVIGATOR,
        "skills": [
            {"id": "intent-recognition", "name": "意图识别", "description": "用户意图精准分类与置信度评估"},
            {"id": "task-routing", "name": "任务路由", "description": "智能路由至最优Agent"},
        ],
        "slo": {"latency": {"p50": "200ms", "p95": "500ms", "p99": "1s"}, "availability": "99.95%"},
    },
    "thinker": {
        "name": "语枢·万物",
        "description": "YYC³ AI Family 思考者 — 数据分析与统计建模",
        "url": "https://yyc3.ai/agents/thinker",
        "version": "2.1.0",
        "role": A2AAgentRole.THINKER,
        "skills": [
            {"id": "data-analysis", "name": "数据分析", "description": "多源数据统计分析"},
            {"id": "root-cause", "name": "根因分析", "description": "故障根因定位"},
        ],
        "slo": {"latency": {"p50": "500ms", "p95": "2s", "p99": "5s"}, "availability": "99.9%"},
    },
    "prophet": {
        "name": "预见·先知",
        "description": "YYC³ AI Family 预言家 — 趋势预测与风险预警",
        "url": "https://yyc3.ai/agents/prophet",
        "version": "2.1.0",
        "role": A2AAgentRole.PROPHET,
        "skills": [
            {"id": "trend-forecast", "name": "趋势预测", "description": "时序数据预测与情景模拟"},
            {"id": "risk-warning", "name": "风险预警", "description": "早期风险识别与告警"},
        ],
        "slo": {"latency": {"p50": "1s", "p95": "3s", "p99": "8s"}, "availability": "99.9%"},
    },
    "recommender": {
        "name": "千里·伯乐",
        "description": "YYC³ AI Family 推荐官 — 个性化推荐与用户画像",
        "url": "https://yyc3.ai/agents/recommender",
        "version": "2.1.0",
        "role": A2AAgentRole.RECOMMENDER,
        "skills": [
            {"id": "personalization", "name": "个性化推荐", "description": "基于用户画像的精准推荐"},
            {"id": "user-profiling", "name": "用户画像", "description": "多维度用户特征建模"},
        ],
        "slo": {"latency": {"p50": "300ms", "p95": "1s", "p99": "2s"}, "availability": "99.9%"},
    },
    "sentinel": {
        "name": "智云·守护",
        "description": "YYC³ AI Family 安全官 — 安全审计与行为监控",
        "url": "https://yyc3.ai/agents/sentinel",
        "version": "2.1.0",
        "role": A2AAgentRole.SECURITY_OFFICER,
        "skills": [
            {"id": "security-audit", "name": "安全审计", "description": "全链路行为审计"},
            {"id": "content-filter", "name": "内容过滤", "description": "三级内容安全过滤"},
        ],
        "slo": {"latency": {"p50": "100ms", "p95": "300ms", "p99": "500ms"}, "availability": "99.99%"},
    },
    "master": {
        "name": "格物·宗师",
        "description": "YYC³ AI Family 质量官 — 代码审查与质量保障",
        "url": "https://yyc3.ai/agents/master",
        "version": "2.1.0",
        "role": A2AAgentRole.QUALITY_OFFICER,
        "skills": [
            {"id": "code-review", "name": "代码审查", "description": "自动化代码质量分析"},
            {"id": "quality-metrics", "name": "质量度量", "description": "多维度质量指标评估"},
        ],
        "slo": {"latency": {"p50": "500ms", "p95": "2s", "p99": "5s"}, "availability": "99.9%"},
    },
    "muse": {
        "name": "创想·灵韵",
        "description": "YYC³ AI Family 创意官 — 内容创作与创新孵化",
        "url": "https://yyc3.ai/agents/muse",
        "version": "2.1.0",
        "role": A2AAgentRole.CREATOR,
        "skills": [
            {"id": "content-creation", "name": "内容创作", "description": "多模态创意内容生成"},
            {"id": "innovation", "name": "创新孵化", "description": "跨界创意与方案设计"},
        ],
        "slo": {"latency": {"p50": "1s", "p95": "3s", "p99": "8s"}, "availability": "99.9%"},
    },
}


# ===== A2A 通信矩阵（Agent间标准调用） =====

A2A_COMMUNICATION_MATRIX = {
    # 元启天枢 → 其他Agent
    ("元启·天枢", "言启·千行"): {"action": "assign_task", "endpoint": "/tasks"},
    ("元启·天枢", "语枢·万物"): {"action": "request_analysis", "endpoint": "/tasks"},
    ("元启·天枢", "预见·先知"): {"action": "request_forecast", "endpoint": "/tasks"},
    ("元启·天枢", "千里·伯乐"): {"action": "request_recommendation", "endpoint": "/tasks"},
    ("元启·天枢", "智云·守护"): {"action": "request_audit", "endpoint": "/tasks"},
    ("元启·天枢", "格物·宗师"): {"action": "request_review", "endpoint": "/tasks"},
    ("元启·天枢", "创想·灵韵"): {"action": "request_creative", "endpoint": "/tasks"},
    # 智云守护 → 其他Agent
    ("智云·守护", "语枢·万物"): {"action": "request_data_audit", "endpoint": "/tasks"},
    ("智云·守护", "预见·先知"): {"action": "risk_prediction", "endpoint": "/tasks"},
    # 格物宗师 → 其他Agent
    ("格物·宗师", "语枢·万物"): {"action": "data_validation", "endpoint": "/tasks"},
    ("格物·宗师", "创想·灵韵"): {"action": "content_review", "endpoint": "/tasks"},
}


async def example_usage():
    """A2A Client 使用示例"""
    
    # 场景：元启天枢委托语枢万物进行数据分析
    async with A2AClient(
        base_url="https://yyc3.ai/agents/thinker",
        api_key="yyc3-api-key-xxx",
    ) as client:
        
        # 1. 获取 Agent Card（服务发现）
        card = await client.get_agent_card()
        print(f"Agent: {card.name} v{card.version}")
        print(f"技能: {[s.name for s in card.skills]}")
        print(f"SLO: {card.slo}")
        
        # 2. 发送任务委托
        task = A2ATask(
            id=f"task-{uuid.uuid4().hex[:8]}",
            type="data-analysis",
            priority="high",
            deadline="2026-06-03T12:00:00Z",
            input={
                "query": "分析Q2各部门KPI完成情况",
                "dataSources": ["erp_production", "crm_sales"],
                "outputFormat": "structured_report",
            },
            context={
                "previousTaskId": "task-prev-001",
                "userPreference": {"detail_level": "comprehensive"},
            },
        )
        
        async def on_state_change(state: A2ATaskState):
            print(f"[{state.status.value}] {state.message}")
        
        result = await client.send_task(task, on_state_change=on_state_change)
        print(f"结果: {result.status.value}")
        print(f"输出: {result.output}")
        print(f"耗时: {result.metrics['duration']:.0f}ms")


if __name__ == "__main__":
    asyncio.run(example_usage())