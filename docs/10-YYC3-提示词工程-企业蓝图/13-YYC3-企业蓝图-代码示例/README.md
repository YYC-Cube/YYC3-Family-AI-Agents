---
file: README.md
description: YYC³ 企业蓝图代码示例族总索引——1300-1308 十大模块工程原型（蓝图文档族 12- 的配套代码实现）
author: YanYuCloudCube Team <admin@0379.email>
version: v1.0.0
created: 2026-11-26
updated: 2026-11-26
status: published
tags: [代码示例],[企业蓝图],[工程原型],[MCP],[A2A],[零信任]
category: architecture
language: zh-CN
audience: ai-engineers
complexity: intermediate
---

# 13- 企业蓝图-代码示例 · 总索引

> ***YanYuCloudCube*** · *言启象限 | 语枢未来*

本族为 [12- 提示词工程-企业蓝图文档族](../12-YYC3-提示词工程-企业蓝图/README.md) 的**配套工程原型**（教学级代码示例，非产线依赖；运行仓产线实现见仓库根 `governance_hub.py` / `agent_server.py` 及 [ARCHITECTURE.md](../../../ARCHITECTURE.md)）。

## 📦 模块清单

| 编号 | 模块 | 内容 | 规模 |
|---|---|---|---|
| 1300 | [核心基础设施](./1300-代码示例-核心基础设施/) | prompt-engine 提示词引擎、AI Family 提示词模板 | 2 py |
| 1301 | [分布式推理](./1301-代码示例-分布式推理/) | 配置与拓扑示例 | — |
| 1302 | [经管运维营](./1302-代码示例-经管运维营/) | 经营决策推理等 | 12 py |
| 1303 | [人资进销存](./1303-代码示例-人资进销存/) | HR/进销存业务示例 | 18 py |
| 1304 | [能力建设智能化](./1304-代码示例-能力建设智能化/) | 标准化/规范化/数据化治理/智能化升级 | 6 py |
| 1304 | [AI-Family-Agent](./1304-代码示例-AI-Family-Agent/) | 八位家人 Agent 原型（千里·伯乐/元启·天枢等） | 8 py |
| 1305 | [价值创造智能化](./1305-代码示例-价值创造智能化/) | 市场洞察/创新孵化等 | 5 py |
| 1306 | [协议栈](./1306-代码示例-协议栈/) | A2A client/server、MCP 示例 | 2 py |
| 1307 | [安全合规](./1307-代码示例-安全合规/) | 零信任网关 zero_trust_gateway | 2 py |
| 1308 | [可观测性](./1308-代码示例-可观测性/) | telemetry 示例 | 1 py |

顶层文件：[API_DOCUMENTATION_V3.md](./API_DOCUMENTATION_V3.md) · docker-compose（单机/全栈）· `test_yyc3_*` 业务验证套件（**教学验收用，不在仓库 CI 范围**。2026-11-26 修复：三套件 sys.path 旧目录名与 smart 套件 2 处脚本 bug 已修——business 验证器全通（"生产就绪"）、smart 全程跑通、full_suite 导入全通；full_suite 尚余 31 例**内容性脱节**（断言键名/方法签名与 v2 实现漂移，如 audit_result→compliance_results、maturity_assessment 已不存在），修复属内容层裁决，以文档演示为准）。

## 📌 说明

- 编号沿用 examples 时期历史体系（1304 双模块为历史既成，遵循「编号不复用不重排」保留原样）。
- 本族原存于仓库根 `examples/13-YYC3-企业蓝图-代码示例/`，2026-11-26 迁入文档库并删除根目录（移动语义完成，本目录为唯一权威副本；git 历史可溯 examples 时期）。

---

> ***YanYuCloudCube***
> *言启象限 | 语枢未来*
> *Words Initiate Quadrants, Language Serves as Core for Future*

**© 2025-2026 YYC³ Team. All Rights Reserved.**
