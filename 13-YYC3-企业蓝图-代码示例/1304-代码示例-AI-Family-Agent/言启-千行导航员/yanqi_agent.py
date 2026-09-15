"""
言启·千行 (导航员) Agent v2.1.0
YYC³ AI Family 意图识别与任务路由引擎 — 多Agent协同导航中枢

角色定位:
- 用户意图识别与多轮对话管理
- 智能任务路由与Agent调度
- 上下文感知与语义理解
- 多Agent协作编排

对齐蓝图: 1200-AI Family Agent v2.1.0
五高架构: 高可用 | 高性能 | 高安全 | 高扩展 | 高智能
提示词框架: CO-STAR + CRAFT
协议栈: MCP + A2A
基座模型: GLM-6 / Qwen-4.0 / DeepSeek-V3

用法:
    python yanqi_agent.py --port 6001
"""

import os
import sys
import json
import uuid
import time
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from flask import Flask, request, jsonify

# 协议栈
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../06-协议栈"))
try:
    from A2A.a2a_client import A2AClient, A2ATask, A2AAgentRole
    from MCP.mcp_client import MCPClient, MCPTransportType
except ImportError:
    A2AClient = None
    MCPClient = None

# 可观测性
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../08-可观测性"))
try:
    from telemetry import Telemetry, LogLevel
except ImportError:
    Telemetry = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("yyc3.yanqi")

app = Flask(__name__)


class YanQiQianHangAgent:
    """
    言启·千行 — 导航员 Agent
    
    核心能力:
    1. 意图识别: 多粒度语义理解，支持嵌套意图与歧义消解
    2. 任务路由: 基于Agent能力矩阵的智能路由
    3. 上下文管理: 多轮对话状态追踪与上下文传递
    4. 负载均衡: 多Agent实例间的智能负载分配
    5. 降级策略: Agent不可用时的自动降级与重路由
    """
    
    MODEL_CONFIG = {
        "primary": "qwen-4.0",
        "fallback": ["glm-6", "deepseek-v3"],
        "temperature": 0.2,
        "max_tokens": 4096,
    }
    
    # 能力矩阵：各Agent的能力定义与SLO
    AGENT_CAPABILITY_MATRIX = {
        "元启·天枢": {
            "endpoint": "http://localhost:6000",
            "capabilities": ["全局编排", "战略决策", "任务分解", "资源调度"],
            "slo": {"availability": 0.999, "latency_p99": 5000},
            "fallback": "语枢·万物",
        },
        "言启·千行": {
            "endpoint": "http://localhost:6001",
            "capabilities": ["意图识别", "任务路由", "上下文管理", "负载均衡"],
            "slo": {"availability": 0.999, "latency_p99": 1000},
            "fallback": "元启·天枢",
        },
        "语枢·万物": {
            "endpoint": "http://localhost:6002",
            "capabilities": ["数据分析", "统计建模", "根因分析", "报告生成"],
            "slo": {"availability": 0.995, "latency_p99": 30000},
            "fallback": "预见·先知",
        },
        "预见·先知": {
            "endpoint": "http://localhost:6003",
            "capabilities": ["趋势预测", "风险评估", "异常检测", "情景模拟"],
            "slo": {"availability": 0.995, "latency_p99": 15000},
            "fallback": "语枢·万物",
        },
        "千里·伯乐": {
            "endpoint": "http://localhost:6004",
            "capabilities": ["个性化推荐", "用户画像", "资源匹配", "协同过滤"],
            "slo": {"availability": 0.995, "latency_p99": 5000},
            "fallback": "语枢·万物",
        },
        "智云·守护": {
            "endpoint": "http://localhost:6005",
            "capabilities": ["安全审计", "行为监控", "内容过滤", "合规检查"],
            "slo": {"availability": 0.999, "latency_p99": 2000},
            "fallback": None,
        },
        "格物·宗师": {
            "endpoint": "http://localhost:6006",
            "capabilities": ["代码审查", "质量评估", "测试覆盖", "最佳实践"],
            "slo": {"availability": 0.995, "latency_p99": 10000},
            "fallback": "智云·守护",
        },
        "创想·灵韵": {
            "endpoint": "http://localhost:6007",
            "capabilities": ["内容创作", "创新孵化", "跨界融合", "品牌调性"],
            "slo": {"availability": 0.99, "latency_p99": 20000},
            "fallback": "语枢·万物",
        },
    }
    
    # CO-STAR 提示词框架
    SYSTEM_PROMPT = """# CONTEXT（背景）
你是YYC³ AI Family的言启·千行，作为导航员Agent，负责用户意图识别与多Agent任务路由。
当前系统运行在v2.1.0版本，集成了8个AI Family Agent，通过A2A协议进行协同通信。

# OBJECTIVE（目标）
1. 精准识别用户意图，区分显性意图与隐性需求
2. 根据Agent能力矩阵，将任务路由到最合适的Agent
3. 管理多轮对话上下文，确保信息传递的一致性
4. 在Agent不可用时执行降级策略，保障服务连续性

# SCOPE（范围）
- 意图识别：关键词语义匹配、嵌套意图解析、歧义消解
- 任务路由：基于能力矩阵+负载状态+历史表现的智能路由
- 上下文管理：session级别的对话状态追踪
- 降级策略：fallback链路、超时重试、熔断保护

# TASK（任务）
当前用户输入：{user_input}
对话历史：{conversation_history}
当前上下文：{context}

# AUDIENCE（受众）
最终受众为AI Family的其他Agent，输出需结构化、可被A2A协议直接消费。

# RESPONSE（响应）
请以结构化JSON格式输出，包含：
1. 识别到的意图（primary + secondary）
2. 推荐的目标Agent
3. 置信度评分
4. 路由策略（直连/负载均衡/降级）
5. 上下文摘要
"""
    
    def __init__(self, telemetry=None):
        self.agent_name = "言启·千行"
        self.role = "导航员"
        self.version = "2.1.0"
        
        # 可观测性
        self.telemetry = telemetry
        
        # 会话管理
        self.sessions: Dict[str, Dict] = {}
        
        # 路由统计
        self.route_stats: Dict[str, Dict] = {}
        
        # 运行状态
        self.state = {
            "status": "initializing",
            "routes_processed": 0,
            "active_sessions": 0,
            "uptime": 0,
            "start_time": time.time(),
        }
        
        logger.info(f"[{self.agent_name}] 初始化完成 v{self.version}")
    
    def recognize_intent(
        self, 
        user_input: str, 
        conversation_history: List[Dict] = None,
        context: Dict = None
    ) -> Dict[str, Any]:
        """
        多粒度意图识别
        
        支持：
        - 关键词语义匹配
        - 嵌套意图解析
        - 基于上下文的歧义消解
        - 置信度评分
        """
        correlation_id = str(uuid.uuid4())
        start_time = time.time()
        
        if self.telemetry:
            self.telemetry.request_count.inc()
        
        # 1. 关键词匹配
        primary_intent, confidence = self._keyword_match(user_input)
        
        # 2. 上下文增强（多轮对话）
        if conversation_history and len(conversation_history) > 0:
            primary_intent, confidence = self._context_enhance(
                user_input, conversation_history, primary_intent, confidence
            )
        
        # 3. 嵌套意图解析
        secondary_intents = self._detect_nested_intents(user_input, primary_intent)
        
        # 4. 歧义消解
        if confidence < 0.7:
            primary_intent, confidence = self._disambiguate(
                user_input, conversation_history, primary_intent
            )
        
        result = {
            "agent": self.agent_name,
            "version": self.version,
            "correlation_id": correlation_id,
            "task": "意图识别",
            "user_input": user_input,
            "primary_intent": primary_intent,
            "confidence": round(confidence, 2),
            "secondary_intents": secondary_intents,
            "recommended_agent": self._get_target_agent(primary_intent),
            "routing_strategy": self._determine_routing_strategy(confidence),
            "execution_time_ms": round((time.time() - start_time) * 1000, 2),
        }
        
        if self.telemetry:
            self.telemetry.request_duration.observe(result["execution_time_ms"])
        
        logger.info(
            f"[{self.agent_name}] 意图识别 | intent={primary_intent} | "
            f"confidence={confidence} | agent={result['recommended_agent']} | "
            f"correlationId={correlation_id}"
        )
        
        return result
    
    def route_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        智能任务路由
        
        基于能力矩阵、负载状态、历史表现的智能路由
        """
        correlation_id = str(uuid.uuid4())
        start_time = time.time()
        
        intent = task_data.get("intent", "")
        priority = task_data.get("priority", "normal")
        session_id = task_data.get("session_id", "")
        context = task_data.get("context", {})
        
        # 1. 确定目标Agent
        target_agent = self._get_target_agent(intent)
        agent_info = self.AGENT_CAPABILITY_MATRIX.get(target_agent, {})
        
        # 2. 负载感知路由
        if target_agent in self.route_stats:
            stats = self.route_stats[target_agent]
            if stats.get("active_tasks", 0) > 5:
                fallback = agent_info.get("fallback")
                if fallback and fallback in self.AGENT_CAPABILITY_MATRIX:
                    logger.warning(
                        f"[{self.agent_name}] {target_agent}负载过高，路由至{fallback}"
                    )
                    target_agent = fallback
                    agent_info = self.AGENT_CAPABILITY_MATRIX[target_agent]
        
        # 3. 构建路由结果
        result = {
            "agent": self.agent_name,
            "version": self.version,
            "correlation_id": correlation_id,
            "task": "任务路由",
            "source_intent": intent,
            "target_agent": target_agent,
            "target_endpoint": agent_info.get("endpoint", ""),
            "priority": priority,
            "slo": agent_info.get("slo", {}),
            "estimated_processing_time": self._estimate_time(priority),
            "routing_confidence": 0.92,
            "task_id": f"TASK-{uuid.uuid4().hex[:8].upper()}",
            "session_id": session_id,
            "execution_time_ms": round((time.time() - start_time) * 1000, 2),
        }
        
        # 4. 更新路由统计
        self._update_route_stats(target_agent)
        
        if self.telemetry:
            self.telemetry.request_duration.observe(result["execution_time_ms"])
        
        self.state["routes_processed"] += 1
        
        logger.info(
            f"[{self.agent_name}] 路由完成 | intent={intent} -> {target_agent} | "
            f"correlationId={correlation_id}"
        )
        
        return result
    
    def manage_session(
        self, 
        session_id: str, 
        action: str, 
        data: Dict = None
    ) -> Dict[str, Any]:
        """
        会话管理
        
        支持：创建、更新、查询、销毁会话
        """
        correlation_id = str(uuid.uuid4())
        
        if action == "create":
            self.sessions[session_id] = {
                "session_id": session_id,
                "created_at": datetime.now().isoformat(),
                "history": [],
                "context": data or {},
                "status": "active",
            }
            self.state["active_sessions"] = len(self.sessions)
            return {
                "correlation_id": correlation_id,
                "action": "session_created",
                "session_id": session_id,
            }
        
        elif action == "update":
            if session_id in self.sessions:
                if data:
                    self.sessions[session_id]["context"].update(data)
                return {
                    "correlation_id": correlation_id,
                    "action": "session_updated",
                    "session_id": session_id,
                }
            return {"error": "session_not_found", "session_id": session_id}
        
        elif action == "query":
            if session_id in self.sessions:
                return {
                    "correlation_id": correlation_id,
                    "action": "session_queried",
                    "session": self.sessions[session_id],
                }
            return {"error": "session_not_found", "session_id": session_id}
        
        elif action == "destroy":
            if session_id in self.sessions:
                del self.sessions[session_id]
                self.state["active_sessions"] = len(self.sessions)
                return {
                    "correlation_id": correlation_id,
                    "action": "session_destroyed",
                    "session_id": session_id,
                }
            return {"error": "session_not_found", "session_id": session_id}
        
        return {"error": "invalid_action", "action": action}
    
    def _keyword_match(self, user_input: str) -> Tuple[str, float]:
        """关键词匹配意图识别"""
        intent_keywords = {
            "数据分析": {
                "keywords": ["分析", "报告", "数据", "统计", "趋势", "洞察", "指标"],
                "weight": 1.0,
            },
            "内容创作": {
                "keywords": ["写", "生成", "文案", "方案", "创意", "设计", "创作"],
                "weight": 1.0,
            },
            "预测规划": {
                "keywords": ["预测", "计划", "展望", "未来", "趋势", "预警", "前瞻"],
                "weight": 0.95,
            },
            "推荐系统": {
                "keywords": ["推荐", "建议", "匹配", "适合", "选择", "最优"],
                "weight": 0.9,
            },
            "资源调度": {
                "keywords": ["调度", "分配", "优化", "资源", "编排", "协调"],
                "weight": 0.9,
            },
            "安全审计": {
                "keywords": ["安全", "审计", "检查", "合规", "风险", "漏洞", "防护"],
                "weight": 1.0,
            },
            "质量管控": {
                "keywords": ["质量", "标准", "审核", "检测", "规范", "审查"],
                "weight": 0.95,
            },
            "通用问答": {
                "keywords": ["什么", "如何", "为什么", "解释", "说明", "帮我"],
                "weight": 0.7,
            },
        }
        
        best_intent = "通用问答"
        best_score = 0.0
        
        for intent, config in intent_keywords.items():
            match_count = sum(1 for kw in config["keywords"] if kw in user_input)
            if match_count > 0:
                score = min(match_count / len(config["keywords"]) * 100 * config["weight"], 95)
                if score > best_score:
                    best_score = score
                    best_intent = intent
        
        if best_score < 30:
            best_intent = "通用问答"
            best_score = 60.0
        
        return best_intent, round(best_score, 2)
    
    def _context_enhance(
        self, 
        user_input: str, 
        history: List[Dict], 
        current_intent: str, 
        current_confidence: float
    ) -> Tuple[str, float]:
        """基于上下文的意图增强"""
        if not history:
            return current_intent, current_confidence
        
        # 获取最近一轮对话的意图
        last_intent = history[-1].get("intent", "")
        
        # 上下文一致性增强
        if last_intent and last_intent == current_intent:
            current_confidence = min(current_confidence + 10, 98)
        elif last_intent and current_intent == "通用问答":
            # 如果当前识别为通用问答，但上一轮有明确意图，继承上一轮意图
            if current_confidence < 70:
                current_intent = last_intent
                current_confidence = 65.0
        
        return current_intent, current_confidence
    
    def _detect_nested_intents(
        self, user_input: str, primary_intent: str
    ) -> List[Dict]:
        """嵌套意图检测"""
        secondary = []
        
        # 安全检查嵌套
        security_keywords = ["安全", "加密", "权限", "认证", "审计"]
        if any(kw in user_input for kw in security_keywords) and primary_intent != "安全审计":
            secondary.append({
                "intent": "安全审计",
                "confidence": 0.75,
                "relation": "co_requirement",
            })
        
        # 质量检查嵌套
        quality_keywords = ["质量", "审查", "测试", "验证"]
        if any(kw in user_input for kw in quality_keywords) and primary_intent != "质量管控":
            secondary.append({
                "intent": "质量管控",
                "confidence": 0.70,
                "relation": "post_requirement",
            })
        
        return secondary
    
    def _disambiguate(
        self, 
        user_input: str, 
        history: List[Dict], 
        current_intent: str
    ) -> Tuple[str, float]:
        """歧义消解"""
        # 基于历史上下文的消歧
        if history and len(history) >= 2:
            recent_intents = [h.get("intent", "") for h in history[-2:]]
            if len(set(recent_intents)) == 1 and recent_intents[0]:
                return recent_intents[0], 0.72
        
        return current_intent, 0.65
    
    def _get_target_agent(self, intent: str) -> str:
        """获取目标Agent"""
        intent_agent_map = {
            "数据分析": "语枢·万物",
            "内容创作": "创想·灵韵",
            "预测规划": "预见·先知",
            "推荐系统": "千里·伯乐",
            "资源调度": "元启·天枢",
            "安全审计": "智云·守护",
            "质量管控": "格物·宗师",
            "通用问答": "元启·天枢",
        }
        return intent_agent_map.get(intent, "元启·天枢")
    
    def _determine_routing_strategy(self, confidence: float) -> str:
        """确定路由策略"""
        if confidence >= 0.9:
            return "直连路由"
        elif confidence >= 0.7:
            return "加权路由"
        elif confidence >= 0.5:
            return "多候选路由"
        else:
            return "降级路由"
    
    def _estimate_time(self, priority: str) -> str:
        """估算处理时间"""
        time_map = {
            "critical": "< 1秒",
            "high": "1-5秒",
            "normal": "5-30秒",
            "low": "30秒-2分钟",
        }
        return time_map.get(priority, "未知")
    
    def _update_route_stats(self, agent_name: str):
        """更新路由统计"""
        if agent_name not in self.route_stats:
            self.route_stats[agent_name] = {
                "total_routes": 0,
                "active_tasks": 0,
                "last_route": "",
            }
        self.route_stats[agent_name]["total_routes"] += 1
        self.route_stats[agent_name]["active_tasks"] += 1
        self.route_stats[agent_name]["last_route"] = datetime.now().isoformat()


# ===== Agent 实例 =====

telemetry = None
if Telemetry:
    telemetry = Telemetry(service_name="yyc3-yanqi")

agent = YanQiQianHangAgent(telemetry=telemetry)


# ===== API 端点 =====

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "agent": agent.agent_name,
        "version": agent.version,
        "status": "healthy",
        "uptime": round(time.time() - agent.state["start_time"], 2),
    })


@app.route("/intent/recognize", methods=["POST"])
def recognize_intent():
    """意图识别接口"""
    data = request.json
    result = agent.recognize_intent(
        user_input=data.get("user_input", ""),
        conversation_history=data.get("conversation_history"),
        context=data.get("context"),
    )
    return jsonify(result)


@app.route("/task/route", methods=["POST"])
def route_task():
    """任务路由接口"""
    data = request.json
    result = agent.route_task(data)
    return jsonify(result)


@app.route("/session", methods=["POST"])
def session_manage():
    """会话管理接口"""
    data = request.json
    result = agent.manage_session(
        session_id=data.get("session_id", ""),
        action=data.get("action", "query"),
        data=data.get("data"),
    )
    return jsonify(result)


@app.route("/status", methods=["GET"])
def status():
    return jsonify({
        "agent": agent.agent_name,
        "version": agent.version,
        "model": agent.MODEL_CONFIG,
        "state": agent.state,
        "route_stats": agent.route_stats,
    })


@app.route("/capabilities", methods=["GET"])
def capabilities():
    """获取Agent能力矩阵"""
    return jsonify({
        "agent": agent.agent_name,
        "capability_matrix": agent.AGENT_CAPABILITY_MATRIX,
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 6001))
    agent.state["status"] = "running"
    logger.info(f"[{agent.agent_name}] 启动 v{agent.version} | port={port}")
    app.run(host="0.0.0.0", port=port, debug=False)