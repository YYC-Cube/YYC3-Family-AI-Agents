# YYC³ FAmily-AI · 规模化预案（E3-5）

> 状态：**预案已预置，执行为部署侧决策**。本文档是 E3-5 的交付物——两条路径的决策矩阵、
> 触发条件与执行清单；数据面迁移开关已在 `governance_hub.py` 预置（`YYC3_DB_BACKEND`）。

---

## 1. 路径决策矩阵

| 维度 | 路径 A：DGX 纵向优化 | 路径 B：K8s + Helm 横向 |
|---|---|---|
| 触发条件 | 单机 TPS 增长 ≤ 3×、负载以推理为主 | 多租户/多业务域扩张、TPS 增长 > 3× |
| 动作 | vLLM 连续批处理调优 · Embedding/Reranker 共卡部署 · systemd 服务内存上限调优 | hub 无状态化 + 8 Agent 水平扩缩 · MCP stateless 路由（协议天然支持）· GPU 资源池化 |
| 数据面 | SQLite WAL 维持（单写者语义不变） | **Postgres 迁移**（开关 `YYC3_DB_BACKEND=postgres`） |
| 风险 | 单机故障域 | 迁移复杂度 · 有状态服务（语义记忆）迁移 |

**默认路径**：A（与现有 DGX Spark N2 生产形态一致）；B 的前置条件 = Postgres 迁移演练完成。

## 2. Postgres 迁移开关（已预置）

- 开关：`YYC3_DB_BACKEND`（`sqlite` 默认 ｜ `postgres` 预留）
- 当前行为：非 sqlite 取值仅产生 warning 日志（提示迁移剧本），**不改变存储**——防止未演练直接切换
- 迁移剧本（执行时序）：双写演练（SQLite 主 + Postgres 影子）→ 行数/校验和对账 → 读切换 → 写切换 → SQLite 转冷备
- 涉及表：`behavior_events` · `token_usage` · `agent_state` · `collaboration_log` · `context_entities` · `context_relations` · `semantic_memory` · `metric_versions` · `golden_candidates` · `durable_steps`

## 3. MCP stateless 路由说明

`/mcp` 端点按 2026-07-28 规范以 **stateless core** 实现（单 POST JSON-RPC、无会话粘滞）——
天然适配水平扩缩：任意副本可服务任意请求，无需会话路由层。
Agent 侧 `/chat`、`/chat/stream`、`/a2a` 的状态（语义缓存 / durable checkpoint / 任务簿）
当前为**单机本地态**——横向扩缩前须完成：语义缓存共享化（Redis/PG）· durable checkpoint
迁 Postgres · A2A 任务簿共享化（三项均列入迁移剧本，未完成前 B 路径只扩推理层不扩状态层）。

## 4. 部署侧验收清单（执行任一路径前逐项确认）

- [ ] 基线压测：目标 TPS 下 p95 延迟与 Token 成本记录
- [ ] 迁移演练：双写对账通过（行数 + 抽样校验和）
- [ ] 故障演练：主端点 failover ≤ 30s（E1-3 降级矩阵）· checkpoint 断点恢复（E3-3）
- [ ] 回滚预案：切换后异常 → 单变量回退（`YYC3_DB_BACKEND` / 摘除新副本）
- [ ] 审计连续：切换窗口内 correlation_id 无断链（治理中枢独有卖点不因迁移丢失）
