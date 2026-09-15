"""
YYC³ MCP (Model Context Protocol) 客户端 v1.0
基于 MCP 2026 标准的工具连接协议实现

核心理念:
- AI的USB-C：标准化工具连接，即插即用
- 支持 Streamable HTTP + SSE / stdio 双传输模式
- 工具发现、资源访问、提示词模板三大能力

对齐蓝图: 1207-协议栈标准化设计
五高架构: 高可用 | 高性能 | 高安全 | 高扩展 | 高智能

用法:
    from mcp_client import MCPClient, MCPTransportType
    
    client = MCPClient("http://localhost:30201", transport=MCPTransportType.STREAMABLE_HTTP)
    tools = await client.list_tools()
    result = await client.call_tool("query", {"sql": "SELECT * FROM sales"})
"""

import json
import uuid
import time
import logging
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import asyncio
import aiohttp

logger = logging.getLogger("yyc3.mcp")


class MCPTransportType(Enum):
    """MCP 传输类型"""
    STREAMABLE_HTTP = "streamable-http"  # HTTP + SSE 远程传输
    STDIO = "stdio"                      # 本地进程通信


class MCPSecurityLevel(Enum):
    """MCP 安全等级"""
    PUBLIC = "public"
    INTERNAL = "internal"  
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


@dataclass
class MCPToolDefinition:
    """MCP 工具定义"""
    name: str
    description: str
    inputSchema: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    securityLevel: MCPSecurityLevel = MCPSecurityLevel.INTERNAL


@dataclass
class MCPResource:
    """MCP 资源定义"""
    uri: str
    name: str
    description: str = ""
    mimeType: str = "text/plain"
    size: Optional[int] = None


@dataclass
class MCPToolResult:
    """MCP 工具调用结果"""
    content: List[Dict[str, Any]] = field(default_factory=list)
    isError: bool = False
    executionTime: float = 0.0
    correlationId: str = ""


@dataclass
class MCPPromptTemplate:
    """MCP 提示词模板"""
    name: str
    description: str
    arguments: List[Dict[str, Any]] = field(default_factory=list)


class MCPClient:
    """
    MCP 协议客户端
    
    实现工具发现、工具调用、资源访问、提示词模板四大能力。
    支持 Streamable HTTP + SSE 和 stdio 两种传输模式。
    内置 correlationId 全链路追踪和安全日志。
    """
    
    def __init__(
        self,
        server_url: str,
        transport: MCPTransportType = MCPTransportType.STREAMABLE_HTTP,
        timeout: int = 30,
        retry_count: int = 3,
        api_key: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ):
        self.server_url = server_url.rstrip("/")
        self.transport = transport
        self.timeout = timeout
        self.retry_count = retry_count
        self.api_key = api_key
        self.correlation_id = correlation_id or str(uuid.uuid4())
        
        self._session: Optional[aiohttp.ClientSession] = None
        self._tools: Dict[str, MCPToolDefinition] = {}
        self._resources: Dict[str, MCPResource] = {}
        self._initialized = False
        
        logger.info(f"[MCP Client] 初始化完成 | server={server_url} | transport={transport.value} | correlationId={self.correlation_id}")
    
    async def __aenter__(self):
        await self.connect()
        return self
    
    async def __aexit__(self, *args):
        await self.disconnect()
    
    async def connect(self) -> bool:
        """建立连接并初始化"""
        if self._initialized:
            return True
        
        start_time = time.time()
        
        try:
            if self.transport == MCPTransportType.STREAMABLE_HTTP:
                self._session = aiohttp.ClientSession(
                    timeout=aiohttp.ClientTimeout(total=self.timeout),
                    headers=self._build_headers(),
                )
                
                # 握手：initialize
                init_result = await self._send_request("initialize", {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {},
                        "resources": {},
                        "prompts": {},
                    },
                    "clientInfo": {
                        "name": "yyc3-mcp-client",
                        "version": "1.0.0",
                    },
                })
                
                if init_result.get("protocolVersion"):
                    self._initialized = True
                    
                    # 发送 initialized 通知
                    await self._send_notification("notifications/initialized", {})
                    
                    # 预加载工具列表
                    await self._load_tools()
                    await self._load_resources()
                    
                    elapsed = (time.time() - start_time) * 1000
                    logger.info(f"[MCP Client] 连接成功 | tools={len(self._tools)} | resources={len(self._resources)} | latency={elapsed:.0f}ms")
                    return True
            else:
                # stdio 模式（简化实现）
                self._initialized = True
                return True
                
        except Exception as e:
            logger.error(f"[MCP Client] 连接失败: {e}")
            return False
    
    async def disconnect(self):
        """断开连接"""
        if self._session:
            await self._session.close()
            self._session = None
        self._initialized = False
        logger.info(f"[MCP Client] 已断开连接")
    
    async def list_tools(self) -> List[MCPToolDefinition]:
        """列出所有可用工具"""
        if not self._initialized:
            await self.connect()
        
        await self._load_tools()
        return list(self._tools.values())
    
    async def call_tool(
        self,
        name: str,
        arguments: Dict[str, Any],
        on_progress: Optional[Callable[[str], None]] = None,
    ) -> MCPToolResult:
        """调用工具"""
        start_time = time.time()
        call_correlation = str(uuid.uuid4())
        
        try:
            if name not in self._tools:
                await self._load_tools()
            
            if name not in self._tools:
                raise ValueError(f"工具不存在: {name}")
            
            tool_def = self._tools[name]
            
            # 安全级别检查
            if tool_def.securityLevel == MCPSecurityLevel.RESTRICTED:
                logger.warning(f"[MCP Client] 调用受限工具: {name} | level={tool_def.securityLevel.value}")
            
            # 参数校验
            self._validate_arguments(tool_def, arguments)
            
            # 发送工具调用请求
            if on_progress:
                on_progress(f"正在调用工具: {name}...")
            
            result = await self._send_request("tools/call", {
                "name": name,
                "arguments": arguments,
            })
            
            execution_time = (time.time() - start_time) * 1000
            
            tool_result = MCPToolResult(
                content=result.get("content", []),
                isError=result.get("isError", False),
                executionTime=execution_time,
                correlationId=call_correlation,
            )
            
            logger.info(
                f"[MCP Client] 工具调用完成 | tool={name} | "
                f"isError={tool_result.isError} | latency={execution_time:.0f}ms | "
                f"correlationId={call_correlation}"
            )
            
            return tool_result
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            logger.error(f"[MCP Client] 工具调用失败 | tool={name} | error={e} | latency={execution_time:.0f}ms")
            
            return MCPToolResult(
                content=[{"type": "text", "text": f"错误: {str(e)}"}],
                isError=True,
                executionTime=execution_time,
                correlationId=call_correlation,
            )
    
    async def list_resources(self) -> List[MCPResource]:
        """列出所有可用资源"""
        if not self._initialized:
            await self.connect()
        
        await self._load_resources()
        return list(self._resources.values())
    
    async def read_resource(self, uri: str) -> str:
        """读取资源内容"""
        if not self._initialized:
            await self.connect()
        
        result = await self._send_request("resources/read", {"uri": uri})
        contents = result.get("contents", [])
        if contents:
            return contents[0].get("text", "")
        return ""
    
    async def list_prompts(self) -> List[MCPPromptTemplate]:
        """列出所有提示词模板"""
        if not self._initialized:
            await self.connect()
        
        result = await self._send_request("prompts/list", {})
        return [
            MCPPromptTemplate(
                name=p.get("name", ""),
                description=p.get("description", ""),
                arguments=p.get("arguments", []),
            )
            for p in result.get("prompts", [])
        ]
    
    async def get_prompt(self, name: str, arguments: Dict[str, str] = None) -> Dict[str, Any]:
        """获取提示词模板"""
        return await self._send_request("prompts/get", {
            "name": name,
            "arguments": arguments or {},
        })
    
    # ===== 私有方法 =====
    
    def _build_headers(self) -> Dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "X-Correlation-ID": self.correlation_id,
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers
    
    async def _send_request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """发送 JSON-RPC 请求"""
        if not self._session:
            raise RuntimeError("MCP Client 未连接")
        
        payload = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": method,
            "params": params,
        }
        
        for attempt in range(self.retry_count):
            try:
                async with self._session.post(
                    f"{self.server_url}/mcp",
                    json=payload,
                ) as resp:
                    data = await resp.json()
                    
                    if "error" in data:
                        error = data["error"]
                        raise Exception(f"MCP Error [{error.get('code')}]: {error.get('message')}")
                    
                    return data.get("result", {})
                    
            except Exception as e:
                if attempt == self.retry_count - 1:
                    raise
                logger.warning(f"[MCP Client] 请求重试 {attempt + 1}/{self.retry_count}: {e}")
                await asyncio.sleep(2 ** attempt)
    
    async def _send_notification(self, method: str, params: Dict[str, Any]):
        """发送通知（无响应）"""
        if not self._session:
            return
        
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
        }
        
        try:
            await self._session.post(f"{self.server_url}/mcp", json=payload)
        except Exception:
            pass  # 通知发送失败不影响主流程
    
    async def _load_tools(self):
        """加载工具列表"""
        result = await self._send_request("tools/list", {})
        self._tools = {
            t["name"]: MCPToolDefinition(
                name=t["name"],
                description=t.get("description", ""),
                inputSchema=t.get("inputSchema", {}),
                tags=t.get("tags", []),
                securityLevel=MCPSecurityLevel(t.get("securityLevel", "internal")),
            )
            for t in result.get("tools", [])
        }
    
    async def _load_resources(self):
        """加载资源列表"""
        result = await self._send_request("resources/list", {})
        self._resources = {
            r["uri"]: MCPResource(
                uri=r["uri"],
                name=r.get("name", ""),
                description=r.get("description", ""),
                mimeType=r.get("mimeType", "text/plain"),
                size=r.get("size"),
            )
            for r in result.get("resources", [])
        }
    
    def _validate_arguments(self, tool_def: MCPToolDefinition, arguments: Dict[str, Any]):
        """校验工具参数"""
        schema = tool_def.inputSchema
        required = schema.get("required", [])
        
        for field in required:
            if field not in arguments:
                raise ValueError(f"缺少必需参数: {field}")


# ===== MCP Server 注册表 =====

YYC3_MCP_SERVERS = {
    "yyc3-db": {
        "name": "yyc3-db-server",
        "description": "YYC³ 数据库查询与写入服务",
        "url": "http://localhost:30201",
        "tools": ["query", "list_tables", "describe_table"],
        "transport": "streamable-http",
    },
    "yyc3-fs": {
        "name": "yyc3-fs-server",
        "description": "YYC³ 文件系统管理服务",
        "url": "http://localhost:30202",
        "tools": ["read_file", "write_file", "list_directory", "delete_file"],
        "transport": "streamable-http",
    },
    "yyc3-knowledge": {
        "name": "yyc3-knowledge-server",
        "description": "YYC³ 知识图谱与向量检索服务",
        "url": "http://localhost:30203",
        "tools": ["semantic_search", "graph_query", "upsert_document"],
        "transport": "streamable-http",
    },
    "yyc3-api": {
        "name": "yyc3-api-server",
        "description": "YYC³ 外部API网关（ERP/CRM连接）",
        "url": "http://localhost:30204",
        "tools": ["call_erp_api", "call_crm_api", "sync_data"],
        "transport": "streamable-http",
    },
    "yyc3-security": {
        "name": "yyc3-security-server",
        "description": "YYC³ 安全扫描与合规检查服务",
        "url": "http://localhost:30205",
        "tools": ["security_scan", "compliance_check", "audit_query"],
        "transport": "streamable-http",
        "securityLevel": "restricted",
    },
    "yyc3-analytics": {
        "name": "yyc3-analytics-server",
        "description": "YYC³ 数据分析与统计服务",
        "url": "http://localhost:30206",
        "tools": ["analyze", "forecast", "visualize"],
        "transport": "streamable-http",
    },
    "yyc3-notification": {
        "name": "yyc3-notification-server",
        "description": "YYC³ 消息推送与告警服务",
        "url": "http://localhost:30207",
        "tools": ["send_message", "send_alert", "query_history"],
        "transport": "streamable-http",
    },
    "yyc3-code": {
        "name": "yyc3-code-server",
        "description": "YYC³ 代码执行与沙箱服务",
        "url": "http://localhost:30208",
        "tools": ["execute_code", "run_tests", "lint_code"],
        "transport": "streamable-http",
        "securityLevel": "restricted",
    },
}


# ===== 使用示例 =====

async def example_usage():
    """MCP Client 使用示例"""
    
    # 1. 创建客户端并连接
    async with MCPClient(
        server_url="http://localhost:30201",
        transport=MCPTransportType.STREAMABLE_HTTP,
        api_key="yyc3-api-key-xxx",
    ) as client:
        
        # 2. 列出所有工具
        tools = await client.list_tools()
        print(f"可用工具: {len(tools)} 个")
        for tool in tools:
            print(f"  - {tool.name}: {tool.description}")
        
        # 3. 调用工具
        result = await client.call_tool("query", {
            "sql": "SELECT department, SUM(revenue) as total FROM sales WHERE month='2026-05' GROUP BY department"
        })
        print(f"查询结果: {result.content}")
        print(f"执行时间: {result.executionTime:.0f}ms")
        print(f"追踪ID: {result.correlationId}")
        
        # 4. 列出资源
        resources = await client.list_resources()
        print(f"可用资源: {len(resources)} 个")
        
        # 5. 获取提示词模板
        prompts = await client.list_prompts()
        print(f"提示词模板: {len(prompts)} 个")


if __name__ == "__main__":
    asyncio.run(example_usage())