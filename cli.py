#!/usr/bin/env python3
"""YYC³ FAmily-AI CLI（docs/13- 路径 C：pip 包入口）

三个入口（pyproject [project.scripts]）：
  yyc3-chat  — 对运行中 agent 端点发起对话（stdlib urllib，零依赖客户端）
  yyc3-audit — 治理库审计链检索（--db 指定 governance.db，静态单行 SQL）
  yyc3-mdl   — 语义层 MDL 校验（load + 指标清单输出）

零强制依赖：全部 stdlib（urllib/sqlite3/tomllib 不涉及）+ 仓内零依赖模块。
SSRF 边界同 evals 契约：http/https 白名单 + 禁内嵌凭据 + 阻断链路本地/保留地址；
环回/私网为本工具显式设计目标（本地 agent 端口）。
"""
import argparse
import ipaddress
import json
import socket
import sqlite3
import sys
import urllib.request
from pathlib import Path
from urllib.parse import urlsplit


def _validate_url(url: str) -> str:
    parts = urlsplit(url)
    if parts.scheme not in ("http", "https") or not parts.hostname:
        raise ValueError(f"仅允许 http/https 且须含主机: {url}")
    if parts.username or parts.password:
        raise ValueError(f"禁止 URL 内嵌凭据: {url}")
    if parts.hostname.lower() != "localhost" and not parts.hostname.startswith("127."):
        for info in socket.getaddrinfo(parts.hostname, None):
            ip = ipaddress.ip_address(info[4][0])
            if ip.is_link_local or ip.is_reserved:
                raise ValueError(f"目标解析到链路本地/保留地址，已阻断: {ip}")
    return url


def chat(args):
    url = _validate_url(f"{args.endpoint.rstrip('/')}/chat")
    payload = json.dumps({"message": args.message, "risk": args.risk}, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=payload,
                                 headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=args.timeout) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    response = data.get("response")
    if isinstance(response, dict):
        print(json.dumps(response, ensure_ascii=False))
        return 1
    print(response)
    return 0


def audit(args):
    db = Path(args.db)
    if not db.exists():
        print(f"治理库不存在: {db}", file=sys.stderr)
        return 2
    conn = sqlite3.connect(str(db))
    try:
        if args.agent:
            rows = conn.execute("SELECT agent, action, details, correlation_id, timestamp FROM behavior_events WHERE agent = ? ORDER BY id DESC LIMIT ?", (args.agent, args.limit)).fetchall()
        else:
            rows = conn.execute("SELECT agent, action, details, correlation_id, timestamp FROM behavior_events ORDER BY id DESC LIMIT ?", (args.limit,)).fetchall()
    finally:
        conn.close()
    out = [dict(zip(["agent", "action", "details", "correlation_id", "timestamp"], r)) for r in rows]
    print(json.dumps(out, ensure_ascii=False, indent=1))
    return 0


def mdl_validate(args):
    import semantic_layer
    from semantic_layer import SemanticLayer
    layer = SemanticLayer.load(args.file)
    out = {"status": "ok", "name": layer.mdl.get("name"),
           "row_limit": layer.row_limit,
           "tables": sorted(layer.tables),
           "metrics": sorted(semantic_layer.METRIC_REGISTRY)}
    print(json.dumps(out, ensure_ascii=False, indent=1))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="YYC³ FAmily-AI CLI")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_chat = sub.add_parser("chat", help="对运行中 agent 端点发起对话")
    p_chat.add_argument("--endpoint", required=True, help="agent 基址（如 http://localhost:25602）")
    p_chat.add_argument("--message", required=True)
    p_chat.add_argument("--risk", default="low")
    p_chat.add_argument("--timeout", type=int, default=90)
    p_chat.set_defaults(func=chat)

    p_audit = sub.add_parser("audit", help="治理库审计链检索")
    p_audit.add_argument("--db", required=True, help="governance.db 路径")
    p_audit.add_argument("--agent", default="")
    p_audit.add_argument("--limit", type=int, default=50)
    p_audit.set_defaults(func=audit)

    p_mdl = sub.add_parser("mdl", help="语义层 MDL 校验")
    p_mdl.add_argument("--file", required=True)
    p_mdl.set_defaults(func=mdl_validate)

    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
