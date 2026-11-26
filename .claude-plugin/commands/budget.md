---
name: budget
description: 查看 YYC³ 八位家人 Token 预算仪表盘（日/周/月窗口与熔断阈值）
---

# /budget — Token 预算仪表盘

查看 8 位家人（meta-oracle / navigator / thinker / prophet / bolero / sentinel / master / creative）的日/周/月预算窗口用量与降级/熔断阈值。

## 执行

```bash
curl -s "http://localhost:25700/budget/dashboard" \
  -H "X-API-Key: ${YYC3_MCP_KEY}" | python3 -m json.tool
```

## 输出要求

1. 表格呈现：家人 / 日用量与限额（百分比）/ 周月概览；
2. `daily_pct >= 80` 标注「降级区间」、`>= 100` 标注「熔断」（对应 hub should_degrade/should_block 阈值）；
3. 超限家人给出治理建议（限流/降级路径），不代为执行任何熔断操作。
