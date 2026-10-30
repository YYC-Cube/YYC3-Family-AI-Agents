#!/usr/bin/env python3
"""E2-1 MCP 客户端 — stateless JSON-RPC 2.0（对齐 2026-07-28 子集）

与 governance_hub 的 /mcp 端点回环联调；亦可用于任意标准 MCP server。
SSRF 边界：仅 http/https；禁内嵌凭据；解析后阻断链路本地/保留地址（含云元数据）；
环回与私网为显式设计目标（本地治理中枢 25700）。
"""
import ipaddress
import json
import socket
import urllib.error
import urllib.request
import uuid
from urllib.parse import urlsplit


class McpTransportError(Exception):
    """HTTP 层失败（非 2xx/202）"""


class McpProtocolError(Exception):
    """JSON-RPC error 响应"""

    def __init__(self, code: int, message: str):
        super().__init__(f"[{code}] {message}")
        self.code = code
        self.message = message


def _validate_url(url: str) -> str:
    parts = urlsplit(url)
    if parts.scheme not in ("http", "https") or not parts.hostname:
        raise ValueError(f"仅允许 http/https 且须含主机: {url}")
    if parts.username or parts.password:
        raise ValueError(f"禁止 URL 内嵌凭据: {url}")
    if parts.hostname.lower() != "localhost":
        for info in socket.getaddrinfo(parts.hostname, None):
            ip = ipaddress.ip_address(info[4][0])
            if ip.is_link_local or ip.is_reserved:
                raise ValueError(f"目标解析到链路本地/保留地址，已阻断: {parts.hostname} -> {ip}")
    return url


class McpClient:
    """无状态 MCP 客户端：每次调用独立 JSON-RPC 请求；correlation_id 经请求头贯穿"""

    def __init__(self, endpoint: str, api_key: str = "", timeout: int = 30,
                 correlation_id: str = None):
        # endpoint 为 MCP 端点完整 URL（如 http://localhost:25700/mcp）
        self.endpoint = _validate_url(endpoint.rstrip("/"))
        self.api_key = api_key
        self.timeout = timeout
        self.correlation_id = correlation_id or str(uuid.uuid4())
        self._next_id = 0

    def _headers(self) -> dict:
        h = {"Content-Type": "application/json", "X-Correlation-ID": self.correlation_id}
        if self.api_key:
            h["X-API-Key"] = self.api_key
        return h

    def _rpc(self, method: str, params: dict = None):
        self._next_id += 1
        body = {"jsonrpc": "2.0", "id": self._next_id, "method": method}
        if params is not None:
            body["params"] = params
        url = _validate_url(self.endpoint)
        req = urllib.request.Request(url, data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
                                     headers=self._headers(), method="POST")
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                status = resp.status
                raw = resp.read().decode("utf-8")
        except urllib.error.HTTPError as e:
            raise McpTransportError(f"{e.code} {e.reason}") from e
        except urllib.error.URLError as e:
            raise McpTransportError(str(e.reason)) from e
        if status == 202:
            return None
        data = json.loads(raw)
        if isinstance(data, dict) and "error" in data:
            err = data["error"]
            raise McpProtocolError(err.get("code", -32000), err.get("message", ""))
        return data.get("result") if isinstance(data, dict) else data

    def initialize(self) -> dict:
        return self._rpc("initialize", {})

    def ping(self):
        return self._rpc("ping")

    def tools_list(self) -> dict:
        return self._rpc("tools/list")

    def tools_call(self, name: str, arguments: dict = None, correlation_id: str = None) -> dict:
        saved = self.correlation_id
        if correlation_id:
            self.correlation_id = correlation_id
        try:
            return self._rpc("tools/call", {"name": name, "arguments": arguments or {}})
        finally:
            self.correlation_id = saved
