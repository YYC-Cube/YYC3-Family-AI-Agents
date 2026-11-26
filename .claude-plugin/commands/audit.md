---
name: audit
description: 检索 YYC³ 治理中枢审计链（按家人过滤 / 全家族最近事件）
---

# /audit — 治理中枢审计检索

按治理中枢审计链检索事件（audit/预算/护栏/协同/MCP 工具调用全量留痕）。

## 执行

```bash
curl -s "http://localhost:25700/audit/trail?agent=${1:-}&limit=${2:-20}" \
  -H "X-API-Key: ${YYC3_MCP_KEY}" | python3 -m json.tool
```

## 输出要求

1. 以表格呈现：时间 / agent / action / risk / correlation_id；
2. 高危事件（risk=high/critical）置顶并标注；
3. 若连接失败，提示检查治理中枢 `:25700` 健康状态（`/health`）与 `YYC3_MCP_KEY` 配置。
