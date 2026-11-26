---
name: freeze
description: 冻结/解冻指定家人（Kill Switch，高危操作须用户二次确认）
---

# /freeze — Kill Switch 一键冻结（高危）

用法：`/freeze <英文id> [reason]`（id ∈ meta-oracle / navigator / thinker / prophet / bolero / sentinel / master / creative；`ALL` 全家族）。

## 执行前必做（契约：高危操作先确认）

向用户复述：目标家人、冻结原因、影响面（该家人对话/委托将返回 frozen 403），**获得明确确认后才执行**。

## 执行

```bash
curl -s -X POST http://localhost:25700/kill-switch \
  -H "Content-Type: application/json" -H "X-API-Key: ${YYC3_MCP_KEY}" \
  -d "{\"agent\": \"${1}\", \"reason\": \"${2:-manual}\"}" | python3 -m json.tool
```

## 备注

- 解冻：`POST /unfreeze`（同参数结构）；
- 冻结动作与恢复均全量入审计链（correlation_id 贯穿）；
- kill-switch 刻意不经 MCP 工具面暴露（hub 设计决定），故本命令走 REST 而非 MCP。
