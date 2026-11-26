# YYC³ FAmily-AI · 插件件套（.claude-plugin/）

五位一体：Skills ×8 + Agents ×8（ZCode subagent 定义）+ Commands ×3 + Hooks（注入检测）+ MCP（治理中枢 8 工具）。清单见 `plugin.json`。

## 🔐 MCP 端点安全（2026-11-26 Mimosa L2 复查处置）

- **本地默认 `http://localhost:25700/mcp` 是刻意选择**：产线为单机部署（hub 与插件消费方同机，loopback 流量不出主机，无中间人向量）；本地 hub 无 TLS 终结器，本地改 `https` 会直接断连。
- **远程部署强制 TLS**：当 hub 与消费方跨机时，**禁止使用 `http://` 明文端点**——必须经 TLS 终结（Nginx/Caddy 反代 + 证书，或 SSH 隧道）后以 `https://` 填入 `plugin.json` / `.mcp.json` 的 `mcpServers.url`，并验证服务端证书。该要求与 docs/14- B9（跨网 A2A：Card security 声明 + TLS/反代）同一治理线。
- **密钥**：一律经 `${YYC3_MCP_KEY}` 环境变量注入，任何清单文件不得硬编码（契约测试强制）。
- **敏感操作面**：kill-switch 刻意不经 MCP 暴露（hub 设计），仅 REST + 零信任写保护可达。

## 结构

```
.claude-plugin/
├── plugin.json          ← 清单（skills/agents/commands/hooks/mcpServers）
├── .mcp.json            ← MCP server 引用（治理中枢 /mcp）
├── skills/              ← 8 人格入口（含五维价值矩阵主责映射）
├── agents/              ← 8 个 ZCode subagent frontmatter 定义
├── commands/            ← audit / budget / freeze（高危二次确认）
└── hooks/               ← guardrails_hook.py（PreToolUse，产线同源规则引擎）
```

契约测试：`tests/unit/test_plugin_suite.py`（7 例，随 CI 全量门禁）。
