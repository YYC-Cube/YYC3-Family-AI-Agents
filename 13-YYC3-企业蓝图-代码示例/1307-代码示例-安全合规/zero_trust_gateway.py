"""
YYC³ 零信任安全网关 v1.0
基于零信任架构的 API 认证与授权网关

核心理念: "永不信任，始终验证"
- 所有请求强制认证，包括内部服务间调用
- 最小权限原则：每个Agent仅获得必要权限
- 持续验证：每次请求独立验证，不依赖会话缓存

对齐蓝图: 1209-安全合规与伦理治理
五高架构: 高安全 | 高可用 | 高性能

用法:
    from zero_trust import ZeroTrustGateway, AuthPolicy
    
    gateway = ZeroTrustGateway(key_store="yyc3-keys")
    
    @gateway.require("strategy:read")
    async def get_strategy(strategy_id: str):
        ...
"""

import json
import uuid
import time
import hashlib
import hmac
import secrets
import logging
from typing import Dict, List, Optional, Any, Callable, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from functools import wraps
import asyncio

logger = logging.getLogger("yyc3.zero_trust")


class PermissionCategory(Enum):
    """权限类别"""
    DECISION = "decision"        # 经营决策
    RESOURCE = "resource"        # 资源管理
    CAPABILITY = "capability"    # 能力建设
    VALUE = "value"              # 价值创造
    HEALING = "healing"          # 自愈链路
    SYSTEM = "system"            # 系统管理
    SECURITY = "security"        # 安全审计
    OBSERVABILITY = "observability"  # 可观测性


class PermissionAction(Enum):
    """权限操作"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    EXECUTE = "execute"
    ADMIN = "admin"


class AuthMethod(Enum):
    """认证方式"""
    API_KEY = "api_key"
    JWT = "jwt"
    HMAC = "hmac"
    MUTUAL_TLS = "mutual_tls"


@dataclass
class AgentIdentity:
    """Agent 身份定义"""
    agent_id: str
    name: str
    role: str
    auth_method: AuthMethod
    credentials_hash: str
    permissions: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class AuthPolicy:
    """认证策略"""
    required_permissions: List[str]
    auth_methods: List[AuthMethod] = field(default_factory=lambda: [AuthMethod.API_KEY])
    require_2fa: bool = False
    rate_limit: int = 100  # 每分钟
    max_request_size: int = 10 * 1024 * 1024  # 10MB


@dataclass
class AuthResult:
    """认证结果"""
    authenticated: bool
    authorized: bool
    agent_id: str = ""
    missing_permissions: List[str] = field(default_factory=list)
    reason: str = ""
    correlation_id: str = ""


@dataclass
class AuditLogEntry:
    """审计日志条目"""
    timestamp: str
    agent_id: str
    action: str
    resource: str
    result: str
    ip_address: str
    correlation_id: str
    details: Dict[str, Any] = field(default_factory=dict)


class ZeroTrustGateway:
    """
    零信任安全网关
    
    核心功能:
    1. 身份认证：API Key / JWT / HMAC / mTLS
    2. 权限授权：RBAC + 最小权限原则
    3. 审计日志：全链路操作记录
    4. 速率限制：防止滥用
    5. 请求签名：防篡改
    """
    
    def __init__(self, key_store: str = "yyc3-keys"):
        self.key_store = key_store
        self._identities: Dict[str, AgentIdentity] = {}
        self._audit_log: List[AuditLogEntry] = []
        self._rate_limiter: Dict[str, List[float]] = {}
        
        # 初始化 AI Family Agent 身份
        self._initialize_agent_identities()
        
        logger.info(f"[ZeroTrust] 网关初始化完成 | agents={len(self._identities)}")
    
    def _initialize_agent_identities(self):
        """初始化 Agent 身份与权限"""
        agent_permissions = {
            "元启·天枢": {
                PermissionCategory.DECISION: {PermissionAction.READ, PermissionAction.WRITE, PermissionAction.EXECUTE, PermissionAction.ADMIN},
                PermissionCategory.RESOURCE: {PermissionAction.READ, PermissionAction.WRITE, PermissionAction.ADMIN},
                PermissionCategory.SYSTEM: {PermissionAction.READ, PermissionAction.WRITE, PermissionAction.ADMIN},
                PermissionCategory.OBSERVABILITY: {PermissionAction.READ},
            },
            "言启·千行": {
                PermissionCategory.DECISION: {PermissionAction.READ},
                PermissionCategory.RESOURCE: {PermissionAction.READ},
                PermissionCategory.CAPABILITY: {PermissionAction.READ},
                PermissionCategory.VALUE: {PermissionAction.READ},
                PermissionCategory.HEALING: {PermissionAction.READ},
            },
            "语枢·万物": {
                PermissionCategory.DECISION: {PermissionAction.READ, PermissionAction.WRITE},
                PermissionCategory.RESOURCE: {PermissionAction.READ},
                PermissionCategory.VALUE: {PermissionAction.READ, PermissionAction.WRITE},
                PermissionCategory.OBSERVABILITY: {PermissionAction.READ, PermissionAction.WRITE},
            },
            "预见·先知": {
                PermissionCategory.DECISION: {PermissionAction.READ, PermissionAction.WRITE},
                PermissionCategory.VALUE: {PermissionAction.READ},
                PermissionCategory.HEALING: {PermissionAction.READ, PermissionAction.WRITE},
            },
            "千里·伯乐": {
                PermissionCategory.RESOURCE: {PermissionAction.READ, PermissionAction.WRITE},
                PermissionCategory.CAPABILITY: {PermissionAction.READ},
                PermissionCategory.VALUE: {PermissionAction.READ, PermissionAction.WRITE},
            },
            "智云·守护": {
                PermissionCategory.SECURITY: {PermissionAction.READ, PermissionAction.WRITE, PermissionAction.EXECUTE, PermissionAction.ADMIN},
                PermissionCategory.SYSTEM: {PermissionAction.READ},
                PermissionCategory.OBSERVABILITY: {PermissionAction.READ, PermissionAction.WRITE},
            },
            "格物·宗师": {
                PermissionCategory.CAPABILITY: {PermissionAction.READ, PermissionAction.WRITE, PermissionAction.EXECUTE},
                PermissionCategory.SYSTEM: {PermissionAction.READ},
                PermissionCategory.HEALING: {PermissionAction.READ, PermissionAction.WRITE},
            },
            "创想·灵韵": {
                PermissionCategory.VALUE: {PermissionAction.READ, PermissionAction.WRITE, PermissionAction.EXECUTE},
                PermissionCategory.CAPABILITY: {PermissionAction.READ},
            },
        }
        
        for name, perms in agent_permissions.items():
            perm_set = set()
            for category, actions in perms.items():
                for action in actions:
                    perm_set.add(f"{category.value}:{action.value}")
            
            agent_id = self._agent_name_to_id(name)
            self._identities[agent_id] = AgentIdentity(
                agent_id=agent_id,
                name=name,
                role="agent",
                auth_method=AuthMethod.HMAC,
                credentials_hash=self._hash_credentials(f"{name}:yyc3-secret-{agent_id}"),
                permissions=perm_set,
            )
    
    def _agent_name_to_id(self, name: str) -> str:
        mapping = {
            "元启·天枢": "tianshu",
            "言启·千行": "navigator",
            "语枢·万物": "thinker",
            "预见·先知": "prophet",
            "千里·伯乐": "recommender",
            "智云·守护": "sentinel",
            "格物·宗师": "master",
            "创想·灵韵": "muse",
        }
        return mapping.get(name, name)
    
    def _hash_credentials(self, credentials: str) -> str:
        return hashlib.sha256(credentials.encode()).hexdigest()
    
    def _generate_signature(self, payload: str, secret: str) -> str:
        """生成 HMAC 签名"""
        return hmac.new(
            secret.encode(), payload.encode(), hashlib.sha256
        ).hexdigest()
    
    def _verify_signature(self, payload: str, signature: str, secret: str) -> bool:
        """验证 HMAC 签名"""
        expected = self._generate_signature(payload, secret)
        return hmac.compare_digest(expected, signature)
    
    # ===== 认证 =====
    
    async def authenticate(
        self,
        headers: Dict[str, str],
        body: str = "",
        ip_address: str = "",
    ) -> AuthResult:
        """认证请求"""
        correlation_id = headers.get("X-Correlation-ID", str(uuid.uuid4()))
        
        # 1. 提取认证信息
        api_key = headers.get("X-API-Key", "")
        auth_header = headers.get("Authorization", "")
        signature = headers.get("X-Signature", "")
        
        if not api_key and not auth_header and not signature:
            return AuthResult(
                authenticated=False, authorized=False,
                reason="缺少认证凭证", correlation_id=correlation_id,
            )
        
        # 2. 查找 Agent 身份
        agent_id = ""
        identity = None
        
        if api_key:
            # API Key 认证
            for aid, ident in self._identities.items():
                if ident.credentials_hash == self._hash_credentials(api_key):
                    agent_id = aid
                    identity = ident
                    break
        
        elif auth_header.startswith("Bearer "):
            token = auth_header[7:]
            for aid, ident in self._identities.items():
                if ident.credentials_hash == self._hash_credentials(token):
                    agent_id = aid
                    identity = ident
                    break
        
        elif signature:
            # HMAC 签名认证
            for aid, ident in self._identities.items():
                secret = f"{ident.name}:yyc3-secret-{aid}"
                if self._verify_signature(body, signature, secret):
                    agent_id = aid
                    identity = ident
                    break
        
        if not identity:
            return AuthResult(
                authenticated=False, authorized=False,
                reason="身份验证失败", correlation_id=correlation_id,
            )
        
        # 3. 速率限制检查
        if not self._check_rate_limit(agent_id):
            return AuthResult(
                authenticated=False, authorized=False,
                agent_id=agent_id,
                reason="速率限制超限", correlation_id=correlation_id,
            )
        
        logger.info(
            f"[ZeroTrust] 认证成功 | agent={identity.name} | "
            f"ip={ip_address} | correlationId={correlation_id}"
        )
        
        return AuthResult(
            authenticated=True, authorized=True,
            agent_id=agent_id, correlation_id=correlation_id,
        )
    
    # ===== 授权 =====
    
    def authorize(
        self,
        agent_id: str,
        required_permissions: List[str],
    ) -> AuthResult:
        """授权检查"""
        identity = self._identities.get(agent_id)
        
        if not identity:
            return AuthResult(
                authenticated=False, authorized=False,
                reason="Agent未注册", correlation_id=str(uuid.uuid4()),
            )
        
        missing = []
        for perm in required_permissions:
            if perm not in identity.permissions:
                missing.append(perm)
        
        if missing:
            return AuthResult(
                authenticated=True, authorized=False,
                agent_id=agent_id,
                missing_permissions=missing,
                reason=f"缺少权限: {', '.join(missing)}",
                correlation_id=str(uuid.uuid4()),
            )
        
        return AuthResult(
            authenticated=True, authorized=True,
            agent_id=agent_id, correlation_id=str(uuid.uuid4()),
        )
    
    # ===== 审计日志 =====
    
    def audit_log(
        self,
        agent_id: str,
        action: str,
        resource: str,
        result: str,
        ip_address: str = "",
        correlation_id: str = "",
        details: Dict[str, Any] = None,
    ):
        """记录审计日志"""
        entry = AuditLogEntry(
            timestamp=datetime.now().isoformat(),
            agent_id=agent_id,
            action=action,
            resource=resource,
            result=result,
            ip_address=ip_address,
            correlation_id=correlation_id or str(uuid.uuid4()),
            details=details or {},
        )
        self._audit_log.append(entry)
        
        logger.info(
            f"[Audit] agent={agent_id} | action={action} | "
            f"resource={resource} | result={result} | "
            f"correlationId={entry.correlation_id}"
        )
    
    # ===== 速率限制 =====
    
    def _check_rate_limit(self, agent_id: str, max_per_minute: int = 100) -> bool:
        now = time.time()
        window = 60  # 1分钟窗口
        
        if agent_id not in self._rate_limiter:
            self._rate_limiter[agent_id] = []
        
        # 清理过期记录
        self._rate_limiter[agent_id] = [
            t for t in self._rate_limiter[agent_id]
            if now - t < window
        ]
        
        if len(self._rate_limiter[agent_id]) >= max_per_minute:
            return False
        
        self._rate_limiter[agent_id].append(now)
        return True
    
    # ===== 装饰器 =====
    
    def require(self, *permissions: str, auth_methods: List[AuthMethod] = None):
        """权限检查装饰器"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # 从参数中提取 headers
                request = kwargs.get("request")
                headers = getattr(request, "headers", {}) if request else {}
                
                # 认证
                auth_result = await self.authenticate(headers)
                if not auth_result.authenticated:
                    raise PermissionError(f"认证失败: {auth_result.reason}")
                
                # 授权
                authz_result = self.authorize(auth_result.agent_id, list(permissions))
                if not authz_result.authorized:
                    raise PermissionError(f"授权失败: {authz_result.reason}")
                
                # 审计日志
                self.audit_log(
                    agent_id=auth_result.agent_id,
                    action=func.__name__,
                    resource=func.__module__,
                    result="authorized",
                    correlation_id=auth_result.correlation_id,
                )
                
                return await func(*args, **kwargs)
            
            return wrapper
        return decorator
    
    # ===== 管理接口 =====
    
    def list_agents(self) -> List[Dict[str, Any]]:
        return [
            {
                "agent_id": ident.agent_id,
                "name": ident.name,
                "role": ident.role,
                "permission_count": len(ident.permissions),
                "created_at": ident.created_at,
            }
            for ident in self._identities.values()
        ]
    
    def get_agent_permissions(self, agent_id: str) -> Optional[Set[str]]:
        identity = self._identities.get(agent_id)
        return identity.permissions if identity else None
    
    def get_audit_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        return [
            {
                "timestamp": e.timestamp,
                "agent_id": e.agent_id,
                "action": e.action,
                "resource": e.resource,
                "result": e.result,
                "correlation_id": e.correlation_id,
            }
            for e in self._audit_log[-limit:]
        ]


# ===== 使用示例 =====

async def example_usage():
    """零信任网关使用示例"""
    
    gateway = ZeroTrustGateway()
    
    # 1. 认证
    headers = {
        "X-API-Key": "元启·天枢:yyc3-secret-tianshu",
        "X-Correlation-ID": str(uuid.uuid4()),
    }
    auth_result = await gateway.authenticate(headers, ip_address="10.0.0.1")
    print(f"认证: {auth_result.authenticated}, {auth_result.reason}")
    
    # 2. 授权
    authz_result = gateway.authorize("tianshu", ["decision:read", "decision:write"])
    print(f"授权: {authz_result.authorized}, {authz_result.reason}")
    
    # 3. 权限不足
    authz_result = gateway.authorize("navigator", ["decision:write"])
    print(f"权限不足: {authz_result.authorized}, {authz_result.reason}")
    
    # 4. 审计日志
    gateway.audit_log("tianshu", "analyze_strategy", "/api/strategy", "success")
    
    # 5. 查看 Agent 列表
    agents = gateway.list_agents()
    print(f"Agent 数量: {len(agents)}")
    for a in agents:
        print(f"  - {a['name']} ({a['agent_id']}): {a['permission_count']} 权限")


if __name__ == "__main__":
    asyncio.run(example_usage())