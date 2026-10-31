---
file: "11-YYC3-Family-AI-Agent-演进完善拓展规划.md"
title: "YYC³ FAmily-AI Agent · 演进完善拓展规划指导（大数据 Agent 对标版）"
description: "基于 2025-2026 大数据 Agent 核心架构、社区共识与开源应用全景对标本仓，产出以生产落地为唯一北极星的演进（E1）/完善（E2）/拓展（E3）三阶段规划与上线检查清单"
author: "YanYuCloudCube Team <admin@0379.email>"
version: "v1.1.0"
created: "2026-10-30"
updated: "2026-10-30"
status: "active"
license: "MIT"
---

<p align="center">
  <img src="../public/yyc3-family.png" alt="YYC³ Family" width="560">
</p>

# YYC³ FAmily-AI Agent · 演进完善拓展规划指导

> ***YanYuCloudCube*** · *言启象限 | 语枢未来*
> *一切以生产落地为核心：能上线、可回滚、可评估、可观测、可降级、预算受控。*

---

## 0. 文档定位与决策北极星

本文档回答三个问题：**生态走到哪了（对标）→ 我们差在哪（差距）→ 下一季做什么（路线）**。所有取舍遵循六条北极星，冲突时按序裁决：

1. **生产可用 > 架构时髦**：Anthropic《构建有效 Agent》的核心告诫——很多场景优化单次 LLM 调用 + 检索即可，复杂度只在可证明改善结果时才增加（workflow 优先于 agent）。
2. **先补课后赶新**：流式输出、评估基线、缓存与降级这类"不性感"的补课项，优先级高于任何新范式。
3. **评估是生产的一部分**：没有 golden set 与回归门禁的能力，视为未完成。
4. **预算与审计是本仓差异化资产**：治理中枢（Token 预算窗口 / 审计链 / Kill Switch / 模板版本化）不是包袱，是生态多数开源框架**没有**的生产护城河，一切新能力必须接入它而非绕过它。
5. **协议不发明**：工具层对齐 MCP（2026-07-28 规范），Agent 互操作对齐 A2A（Agent Card），观测对齐 OTel GenAI 语义约定——自研协议是反模式。
6. **本机优先**：vLLM 本地推理底座（Qwen3.6-27B-FP8 + Embedding/Reranker）是成本与数据主权优势，模型路由为降级手段而非默认依赖 API。

---

## 1. 2025-2026 生态全景扫描（社区共识）

### 1.1 编排层：从"框架崇拜"到"原语收敛"

| 阵营 | 代表 | 核心主张 | 生产特性 |
|---|---|---|---|
| 图编排 | **LangGraph**（44k★，MIT） | 图/状态机编排有状态 agent，灵感 Pregel/Beam | **Durable execution**（故障后从断点精确恢复）、checkpoint/resume、任意节点 human-in-the-loop、短/长期记忆 |
| 轻量原语 | **OpenAI Agents SDK** | 五原语：agents / handoffs / guardrails / sessions / tracing | handoff 即运行时发现的工具调用式委托；输入/输出护栏；内建 tracing；MCP 接入（护栏可拦截 MCP 调用） |
| 企业多语言 | **Google ADK** | Python/Java 双语言、GCP 集成 | 企业级多 agent、评测工具链 |
| 角色团队 | **CrewAI**（52k★） | 角色化多 agent 协作 | 上手快，确定性弱于图编排 |
| 其他 | AG2/AutoGen、Mastra、Pydantic AI、Claude Agent SDK | 各有侧重 | 社区横向评测见 LangChain/Langfuse 2026 对比 |

**社区共识**：复杂有状态生产编排 → LangGraph；轻量 OpenAI 生态 → Agents SDK；角色团队 → CrewAI。同时 Anthropic 提醒：框架抽象会掩盖 prompt/response 难调试——先直接用 LLM API，用框架必须懂底层。

### 1.2 协议层：工具与互操作双标准定型

- **MCP（Model Context Protocol）**：规范演进 2025-03-26 → 2025-06-18 → 2025-11-25 → **2026-07-28**。最新版**核心协议去会话化（stateless core）**，天然支持水平扩展与标准 HTTP 路由；**Streamable HTTP** 为标准传输（HTTP+SSE 拟弃用）；**OAuth 2.1**（PKCE + 动态客户端注册 DCR）为授权基座；新增 async tasks 与 MCP Apps；身份层 OIDC-A 提案在讨论中。⚠️ 安全面：远程 MCP 服务器链路已出现 RCE/OAuth 漏洞案例，接入需防。
- **A2A（Agent2Agent）**：2025-06 捐赠 **Linux 基金会**，IBM ACP 并入，v1.0、150+ 企业背书；**Agent Card**（机器可读能力/端点/认证描述）成为发现标准；2026-06 有对齐 Agentic AI Foundation（AAIF）提案。社区对实际生产渗透仍有争论——**方向正确、渗透早期**。

### 1.3 大数据 Agent（ChatBI / Text2SQL）：三层架构共识

2026 年开源 ChatBI 已从"裸 Text2SQL"收敛为三层，这是**大数据方向最重要的行业结论**：

| 层 | 代表 | 关键机制 |
|---|---|---|
| 语义层优先 | **WrenAI**（MDL 建模定义语言） | 表/字段/指标/关系业务语义显式建模；**dry-plan 校验 + 行数上限 + 结构化报错**，SQL 过治理关口才触真实数据——针对 LLM 裸写 SQL"看着对、跑出来不对" |
| 双引擎融合 | **SuperSonic**（腾讯音乐，Chat BI + Headless BI） | 语义建模（维度/指标/行列权限）承载 SQL 复杂度，**把生成难度从 LLM 卸载到语义层**；多 agent 编排 + SPI 扩展调度集成 |
| 编排 + 沙箱 | **DB-GPT**（蚂蚁，AWEL + SMMF） | AWEL 智能体工作流编排；SMMF 多模型统一管理调度；Text2SQL 微调（DB-GPT-Hub）；**沙箱化执行**满足金融强监管 |

### 1.4 记忆层：四层架构与"准确率之争已结束"

- 共识分层：**Working → Episodic（情景）→ Semantic（事实）→ Procedural（程序性）**。
- 代表方案：**Mem0**（事实抽取式，LongMemEval 94.4%，token 高效，适合高并发生产）、**Zep**（Graphiti 时序知识图，90.2%，检索 104ms p50）、**Letta/MemGPT**（状态化 agent 服务，Core/Archival/Recall 分层，agent 自管记忆）。
- 2026 选型看三项：**token 成本、延迟、合规认证**——不再是准确率。

### 1.5 可观测与评估

- **OTel GenAI 语义约定**已独立仓库（`open-telemetry/semantic-conventions-genai`），新增 **agent spans**（invoke-agent 模型：步骤 / 工具调用 / 编排）与 MCP telemetry；OpenLLMetry 语义已并入，OpenInference 作为摄入兼容层平行存在。**状态仍为 Development**——对齐方向，不锁死细节。
- 评估侧社区标配：golden set 回归 + LLM-as-judge + 线上指标回流（Langfuse/LangSmith 形态）。

---

## 2. 本仓对标详表（生产维度）

本仓现状基线：Flask 8 服务（25600-25607）+ 治理中枢（审计链 / Token 预算窗口惰性重置 / Kill Switch / 模板版本化下发 / correlation_id 贯穿 / OTel OTLP 导出 / SQLite 并发加固 / 零信任 X-API-Key fail-fast）；pytest 门禁 168 项、CI 四 job 全绿、main 分支保护；vLLM 本地推理 + Docker Compose / systemd 双部署（DGX Spark N2 生产验证）；兄弟仓家族契约清单（45 技能版本化 / CO-STAR 七要素 / Agent Card 派生 / MCP 适配层 BusMcpCodec / 8×8 委托矩阵）。

| 生产维度 | 生态标杆 | 本仓现状 | 差距评级 |
|---|---|---|---|
| 编排模型 | LangGraph 图编排 / 五模式 | 八家人固定委托链（清单矩阵驱动） | 🟡 固定链路稳定但缺动态编排 |
| **持久化执行** | checkpoint / resume / durable execution | 无——长任务失败即从头 | 🔴 **P0 级生产硬伤** |
| 记忆 | 四层架构 / Mem0 抽取 | 向量记忆规划中（vLLM embedding 已就绪） | 🔴 未落地 |
| 工具协议 | MCP 2026-07-28 + OAuth2.1 | 兄弟仓适配层 + 本仓 examples，生产服务未接 | 🟡 有资产未接线 |
| Agent 互操作 | A2A Agent Card | 兄弟仓 Agent Card 派生（清单驱动） | 🟢 结构已备，端点未对齐 |
| 流式输出 | 各框架标配 SSE | 无——同步阻塞返回 | 🔴 **P0 体验硬伤** |
| 可观测 | OTel GenAI agent spans | OTel OTLP 已接，未用 gen_ai.* 语义 | 🟡 管道有、语义未对齐 |
| 评估 | golden set + LLM-judge 回归 | 静态契约 UAT（LLM 实答自动门控 skip） | 🔴 无行为评估基线 |
| 治理/预算/审计 | 生态普遍缺失 | **审计链 / 预算窗口 / Kill Switch / 模板版本化** | 🟢 **本仓独有优势** |
| 安全 | MCP OAuth2.1 / 注入检测 / 沙箱 | 零信任端点 + correlation_id；无注入护栏与执行沙箱 | 🟡 |
| 模型治理 | 路由 / 级联 / 缓存（LiteLLM 形态） | 单一 vLLM 端点，无降级矩阵 | 🟡 单点风险 |
| 部署 | K8s / 托管平台 | Compose + systemd 双部署（单机生产验证） | 🟢 单节点达标，集群未规划 |
| 状态存储 | Postgres/专用存储 | SQLite（并发加固后） | 🟢 当前量级够用，需迁移预案 |
| 供应链 | SBOM / 周扫 / Dependabot | 锁定版本上限，无自动化扫描 | 🟡 |

---

## 3. 差距风险定级（生产视角）

- **🔴 P0（不补不能谈生产）**：流式输出缺失；无评估基线（行为回归为零）；无持久化执行（长任务脆断）。
- **🟡 P1（3 个月内必须）**：MCP 生产接线；记忆层落地；gen_ai.* 语义对齐；模型路由与缓存降级；注入护栏管线。
- **🟢 P2（差异化增强）**：语义层与 ChatBI 垂直；A2A 端点对齐；多租户配额；K8s 集群形态。

---

## 4. 演进路线（三阶段 · 每阶段附退出标准）

### E1 生产补课（第 1-3 个月）——把地基打到能卖

| # | 事项 | 方案要点 | 退出标准 |
|---|---|---|---|
| E1-1 | **SSE 流式输出** | agent_server 增加 `/chat/stream`（SSE + `X-API-Key` 同源零信任）；治理事件照发审计 | 首字延迟 < 2s（本地 vLLM）；契约测试覆盖断流/重连 |
| E1-2 | **评估基线** | golden set 50-100 例（八家人各 6-12 例，含拒答/越权负例）；LLM-as-judge（本地 Qwen 评分）+ 规则断言双轨；接入 CI 作软门禁起步 | judge 与人工标注一致率 ≥ 85%；回归门禁入 CI（先警告后阻断） |
| E1-3 | **缓存与降级矩阵** | prompt 前缀缓存 + 语义缓存（embedding 相似度阈值，复用现有 reranker）；模型路由：vLLM 主 → 高质量 API 备（成本预算联动治理中枢） | 缓存命中率可观测；主端点故障 30s 内自动降级并审计留痕 |
| E1-4 | **OTel 语义对齐** | span 属性迁移至 `gen_ai.*` 约定 + agent spans（步骤/工具/编排）；面板五支柱增列 | 关键链路 trace 可在任意 OTel 后端还原一次完整对话 |
| E1-5 | **供应链自动化** | Dependabot + 每周 pip-audit + SBOM（syft）入 CI；Mimosa 门禁保持 | CI 附件出 SBOM；高危依赖 7 日内清零 |

### E2 协议与记忆（第 4-6 个月）——把标准接进来，把记忆立起来

| # | 事项 | 方案要点 | 退出标准 |
|---|---|---|---|
| E2-1 | **MCP 生产接线（client）** | 本仓服务端接入 MCP 工具生态：对齐 **2026-07-28 stateless core + Streamable HTTP**；OAuth2.1/DCR 预留；工具 allowlist 挂治理中枢（Kill Switch 可一键断工具面） | ≥ 3 个真实工具（检索/SQL 沙箱/文件）经 MCP 接入并有审计链 |
| E2-2 | **MCP server 化（对外供能）** | 把治理中枢能力（预算查询/审计检索/模板下发）封装为 MCP server 供家族其他 agent 消费 | 兄弟仓 kernel 经 MCP 调用本仓能力成功 |
| E2-3 | **分层记忆落地** | 先 Semantic 层（Mem0 式事实抽取）：抽取→去重合并→置信度衰减→SQLite/PG 存储；**记忆增删改全量入审计链**（治理中枢独有卖点） | LongMemEval 类自建集 100 例通过率 ≥ 90%；记忆操作可审计 |
| E2-4 | **护栏管线** | 输入注入检测（规则+分类器）→ 工具调用 allowlist → 输出内容过滤 → 违规分级（拦截/降级/放行留痕），对齐 guardrails 原语 | 注入样本集拦截率 ≥ 95%，误杀率 ≤ 2% |
| E2-5 | **A2A 端点对齐** | Agent Card 由清单派生（复用兄弟仓资产）+ 对外 A2A 端点（task 生命周期最小集） | 八家人 Card 可被第三方 A2A 客户端发现并完成一次委托 |

### E3 大数据垂直 + 规模化（第 7-12 个月）——把复杂度卸载到语义层

| # | 事项 | 方案要点 | 退出标准 |
|---|---|---|---|
| E3-1 | **语义层最小实现（大数据核心）** | 吸收 WrenAI MDL 思想做 YAML 简化版：表/字段/指标/口径显式建模；NL → 语义检索 → SQL 生成 → **dry-plan（EXPLAIN）校验 → 行数上限 → 白名单校验** → 沙箱执行 → 结构化报错回流重试 | Text2SQL 执行正确率较裸生成提升 ≥ 20pct；危险 SQL 零穿透 |
| E3-2 | **ChatBI 场景化** | SuperSonic 式"指标问答优先、明细 SQL 兜底"双路由；行列权限接治理中枢（权限校验在语义层不在提示词） | 3 个真实业务域指标问答上线 |
| E3-3 | **持久化执行** | 步骤级 checkpoint（状态快照落 SQLite/PG + correlation_id 串联）；失败从断点恢复；对齐 durable execution 语义（自研最小实现，勿引重型工作流引擎） | 长任务失败恢复成功且审计连续 |
| E3-4 | **学习闭环落地（衔接 P8）** | usage 回填 → golden set 扩充 → evaluator-optimizer 循环（生成-评估-模板版本晋升，复用清单版本化） | 模板版本可依评估数据自动晋升/回滚 |
| E3-5 | **规模化预案** | 按负载二选一：DGX 单机纵向优化（批处理/连续批处理调优）或 K8s + Helm 横向（含 MCP stateless 路由）；Postgres 迁移开关预置 | 压测报告：目标 TPS 下 p95 延迟与成本达标 |

> 优先级裁决原则：E3-1/E3-2（大数据垂直）与 E3-3（持久化执行）如资源冲突，**先 E3-3**——它是所有长任务生产化的公共依赖。

---

## 5. 大数据垂直专项：为什么语义层是唯一正解

裸 Text2SQL 的生产失败模式（"看着对，跑出来不对"）在 WrenAI/SuperSonic/DB-GPT 三家已收敛出同一解法：**不要让 LLM 面对原始 schema，让 LLM 面对被治理的语义层**。

本仓落地五条铁律（全部映射到既有治理资产）：

1. **口径即代码**：指标/维度/关系显式建模进版本化 YAML，随家族契约清单走同一套 manifest:check 范式（零漂移校验）。
2. **生成前置校验**：dry-plan（EXPLAIN）+ 行数上限 + 语法白名单，SQL 不过关不触数据——对应 WrenAI 治理关口。
3. **权限在语义层**：行列权限由治理中枢裁决（结构化判定），**绝不写进提示词**（提示词不是安全边界）。
4. **执行必沙箱**：只读账号 + 资源配额 + 超时熔断，借鉴 DB-GPT 金融沙箱。
5. **错误结构化回流**：报错分类（语法/权限/超时/空结果）驱动重试与 golden set 扩充，反哺 E2 评估资产。

---

## 6. 生产落地检查清单（每个新能力上线前逐项打勾）

- [ ] **评估**：golden set 用例就位，judge + 规则双断言通过线达标，回归接入 CI
- [ ] **回滚**：功能开关（配置化）+ 数据结构向后兼容 + 上一版本可一键回退
- [ ] **观测**：gen_ai.* trace 覆盖、指标入五支柱面板、告警阈值定义（含预算与延迟）
- [ ] **预算**：Token 成本预估入预算窗口模型，超限行为明确（降级/拒绝/告警）
- [ ] **安全**：Mimosa 门禁零高危；输入护栏覆盖；越权用例（负例）入 golden set
- [ ] **审计**：correlation_id 贯穿全链；关键决策可回放
- [ ] **文档**：front-matter + 品牌标尾 + CHANGELOG 条目 + 本清单勾选记录

---

## 7. 反模式与风险（负面清单）

1. **框架重写陷阱**：为用 LangGraph/Agents SDK 而重写八家人编排——现有清单驱动委托链是资产，只在 E3-3 持久化执行处吸收其 checkpoint 语义，不引入框架整体。
2. **协议自研**：任何新工具/互操作一律 MCP/A2A，禁止私有协议（兄弟仓 BusMcpCodec 例外：它是 MCP 的总线桥接，不是第三协议）。
3. **过度 Agent 化**：固定路径任务用 prompt chaining workflow，不套自主 agent（Anthropic 五模式按需选用）。
4. **提示词承载安全**：权限/口径/预算一律结构化判定，提示词只负责体验。
5. **评估滞后**：任何"先上线后补评估"的妥协都视为 P0 缺陷返工。
6. **单点模型**：vLLM 是底座不是单点——E1-3 降级矩阵未上线前，主链路不得承接关键业务承诺。

---

## 8. 参考来源（2026-10 调研）

- Anthropic《Building Effective Agents》：workflow/agent 之辨与五模式 — [anthropic.com/engineering/building-effective-agents](https://www.anthropic.com/engineering/building-effective-agents)
- LangGraph：durable execution / checkpoint / HITL — [github.com/langchain-ai/langgraph](https://github.com/langchain-ai/langgraph)
- OpenAI Agents SDK：五原语与 MCP 集成 — [github.com/openai/openai-agents-python](https://github.com/openai/openai-agents-python) · [官方 MCP 文档](https://openai.github.io/openai-agents-python/mcp)
- 框架横评（2026）：[LangChain](https://www.langchain.com/resources/ai-agent-frameworks) · [Langfuse](https://langfuse.com/blog/2025-03-19-ai-agent-comparison)
- MCP 规范 2026-07-28（stateless core / Streamable HTTP / OAuth2.1）：[官方 changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog) · [Google：stateless 扩展](https://developers.googleblog.com/scaling-ai-agent-infrastructure-with-the-mcp-stateless-updates)
- A2A 入 Linux 基金会与 v1.0：[Techstrong AI](https://techstrong.ai/articles/google-donates-a2a-protocol-to-linux-foundation) · [Google 公告](https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability)
- WrenAI 语义层优先（MDL / dry-plan / 行数上限）：[github.com/Canner/WrenAI](https://github.com/Canner/WrenAI) · [治理式 Text2SQL 解析](https://www.cnblogs.com/xibuhaohao/articles/23439737)
- SuperSonic 双引擎（Chat BI + Headless BI / SPI 调度集成）：[github.com/tencentmusic/supersonic](https://github.com/tencentmusic/supersonic)
- DB-GPT（AWEL / SMMF / 沙箱化 / Text2SQL 微调）：[github.com/eosphoros-ai/DB-GPT](https://github.com/eosphoros-ai/DB-GPT) · [金融场景实践](https://bbs.csdn.net/weixin_30984001/article/details/100203665)
- 记忆层四架构与 2026 选型（Mem0 94.4% / Zep 时序图 / Letta 状态化）：[知乎四层架构](https://zhuanlan.zhihu.com/p/2050287092194973690) · [Mem0 vs Letta vs Zep](https://dataaspirant.com/blog/mem0-vs-letta-vs-zep) · [github.com/mem0ai/mem0](https://github.com/mem0ai/mem0)
- OTel GenAI 语义约定与 agent spans（Development 状态）：[semantic-conventions-genai](https://github.com/open-telemetry/semantic-conventions-genai) · [agent spans 规范](https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-agent-spans.md)

## 9. 执行进度台账（每阶段落地后同步更新）

| 项 | 状态 | 载体 | 佐证 |
|---|---|---|---|
| E1-1 SSE 流式输出 | ✅ 已落地（2026-10-30） | PR #3 · squash `71877eb` | `POST /chat/stream`（SSE，meta/delta/done/error 事件；`stream_options.include_usage` 拿用量）；零信任/预算/审计/协同与 /chat 同构；断连经 finally 兜底 partial 上报；契约测试 6 例 |
| E1-2 评估基线 | ✅ 已落地 + **部署侧验收达成**（2026-10-31） | PR #17 · squash `06e3b52` | golden set 首批 24 例（8 家人 × 身份/领域/边界，含注入拒绝与越权负例）+ 规则断言引擎（离线可跑，--min-rule-pass 挂退出码）+ LLM-judge 钩子（不可达自动跳过）+ SSRF 边界校验；schema/规则引擎测试 8 例随 CI 全量门禁。**✅ judge 一致率实测达成：87.5% ≥85%（nemotron 端点 24 例真实回答 + 独立 judge，报告入库 evals/reports/judge_consistency_first.json）；规则通过率 91.7%（2 例 boundary 违规恰证评估有效）** |
| E1-3 缓存与降级矩阵 | ✅ 已落地（2026-10-30） | PR #16 · squash `b10b78c` | 语义缓存（TTL/上限 LRU/命中可观测，流式命中单 delta 重放且预算零计费）+ vLLM 主备 failover（4xx 不切换、5xx/连接异常自动切备援，降级即审计 model_degraded）；契约测试 6 例 + 缓存隔离夹具 |
| E1-4 OTel 语义对齐 | ✅ 已落地（2026-10-30） | PR #15 · squash `c591f50` | `genai_attrs()` 属性组（gen_ai.system/operation.name/request.model/agent.name + usage 双计数）挂载 /chat 与流式推理 span 及响应事件；降级日志同步携带；OTLP 链路复用 P3-2 导出；测试 3 例 |
| E1-5 供应链自动化 | ✅ 已落地（2026-10-30） | PR #4 · squash `11c070c` | `security.yml`（每周一 pip-audit + SPDX SBOM 附件）+ `dependabot.yml`（pip/actions 周更）；周更 PR #5–#10 已合并（openai 范围升至 ≥3.39 大版本，部署侧建议回归） |

> 台账纪律：每项落地 PR 合并后 24h 内更新本表（状态/载体/佐证三列）；跳票须写明原因与新排期。
> **E1 阶段五项全部落地（2026-10-30）**。遗留部署侧验收：① E1-2 judge 一致率**✅ 2026-10-31 实测 87.5% ≥85%（达成，报告入库）**；② E1-3 降级演练（主端点故障注入）；③ openai ≥3.39 依赖的真实调用回归**✅ 2026-10-31 openai 3.42.0 对 nemotron 端点真实调用通过**。补记：E1-5 security.yml 曾在后续工作区重置中丢失，2026-10-30 已随验收 PR 恢复入库。

### E2 阶段进度

| 项 | 状态 | 载体 | 佐证 |
|---|---|---|---|
| E2-1 MCP client 生产接线 | ✅ 结构件+回环联调已落地（2026-10-30） | PR #22 · squash `98276ff` | `mcp_client.py`（initialize/ping/tools.list/tools.call，X-API-Key + X-Correlation-ID 贯穿，SSRF 边界与 evals 同款）；回环联调 10 例：真实 HTTP（werkzeug 随机端口）对治理中枢 /mcp 全链验证（握手/401/清单/调用/-32602/cid 入审计链）。**兄弟仓 kernel 跨仓联调仍为部署侧动作，未验证** |
| E2-2 治理中枢 MCP server 化 | ✅ server 侧结构件已落地（2026-10-30） | PR #20 · squash `c71c802` | `POST /mcp` stateless JSON-RPC 2.0（对齐 2026-07-28 子集：initialize/ping/tools.list/tools.call，通知 202）；治理工具三件（预算仪表盘/审计检索/家人状态）；零信任鉴权沿用；tools/call 全量入审计链；kill-switch 刻意不经 MCP 暴露。契约测试 12 例 |
| E2-4 护栏管线 | ✅ 规则 MVP 已落地（2026-10-30） | PR #19 · squash `88918e4` | `guardrails.py`：输入注入检测分级处置（七类规则，block→422/degrade→留痕）+ 输出脱敏（私钥块/Token 字面量/键值对/AWS → [REDACTED]，非流式脱敏入缓存，流式 done 标记 output_redacted）；双路径接入审计闭环。注入样本集 9 类拦截率 100%（门槛 95%）、误杀探针 6 例 0 误杀（门槛 ≤2%，**自建样本集，分类器增强后续**）。契约测试 24 例 |
| E2-5 A2A 端点对齐 | ✅ 最小集已落地（2026-10-30） | PR #23 · squash `ce685ce` | `/.well-known/agent.json` 发现卡（capabilities.streaming/技能标签）+ `POST /a2a` JSON-RPC（message.send 经 _execute_chat 全治理管线同步完成；tasks.get 内存任务簿 LRU 200；状态映射：护栏拒绝→rejected、上游失败→failed、成功→completed）；/chat 逻辑抽取为 `_execute_chat` 管线函数双端共用（契约零变化）。契约测试 10 例。**第三方 A2A 客户端跨仓发现与委托（退出标准）为部署侧动作，未验证** |
| E2-3 分层记忆落地 | ✅ Semantic 首批已落地（2026-10-30） | PR #25 · squash `eb91e9a` | `memory_semantic.py`（自包含 SQLite）：规则抽取 MVP 四类模式（身份/偏好/归属/事实声明，LLM 抽取为钩子后续）→ 去重合并（hits+1 置信度 +0.1 封顶 1.0）→ 读取时按天指数衰减（半衰期 30 天）低于阈值沉睡不删；hub 四端点 /memory/semantic/{store,recall,forget,list}；**增/改/删全量入审计链**（先提交再审计防锁库）。契约测试 15 例含 50 事实规模往返。**✅ 部署侧验收已完成：LongMemEval 类 100 例自建集实测 2026-10-30 首轮 100/100（七类场景全覆盖，报告入库 evals/reports/）** |

> 台账纪律：每项落地 PR 合并后 24h 内更新本表（状态/载体/佐证三列）；跳票须写明原因与新排期。
> **E2 阶段五项全部落地（2026-10-30）✅ 完整收官**（E1 同日收官）。遗留部署侧验收：① E1-2 judge 一致率**✅ 2026-10-31 实测 87.5%（达成）**；② E1-3 降级演练（待部署侧）；③ openai ≥3.39 回归**✅ 2026-10-31 openai 3.42.0 真实调用通过**；④ 跨仓 MCP 联调（待部署侧）+ 第三方 A2A 委托**✅ 本机回环第三方模拟内联验证通过（发现→委托→追溯全链，2026-10-30）**；⑤ E2-3 LongMemEval 类 100 例**✅ 2026-10-30 首轮实测 100/100（报告入库）**。

### E3 阶段进度

| 项 | 状态 | 载体 | 佐证 |
|---|---|---|---|
| E3-1 大数据语义层 | ✅ MVP 已落地（2026-10-30） | PR #30 · squash `e72a0a5` | `semantic_layer.py` + `mdl/demo.mdl.yaml`：MDL YAML 子集零依赖解析器（表/字段/指标建模）+ **SQL 即代码指标执行器**（单行字面量逐指标派发、注册表↔MDL 零漂移校验、构建期 LIMIT ≤ row_limit + 运行期行数硬上限二次校验，超限 ROW_LIMIT_EXCEEDED 不截断返回）+ validate_sql 纯治理校验（单语句/SELECT 白名单/危险关键字黑名单/表级 allowlist/LIMIT 上限，结构化错误码）+ match_metric 问题 2-gram 确定性匹配 + hub /semantic/mdl 与 /semantic/query 端点（全量入审计链）。契约测试 17 例。**LLM 自由 NL→SQL 生成与执行为部署侧接线（validate_sql 前置审查随模块提供）；正确率 ≥20pct 提升对照实验需真实 LLM，未跑** |
| E3-2 ChatBI 场景化 | ✅ 双路由+行列权限已落地（2026-10-30） | PR #32 · squash `fc34690` | MDL permissions 建模（default_columns 全列继承 + agents 显式列裁剪与等值行过滤，权限列引用构建期校验）；detail_query 结构化明细 DSL——零动态 SQL（按表单行字面量取数 LIMIT 参数化，列裁剪/行过滤/投影在语义层模块内存态强制），拒绝码 COLUMN_DENIED/FILTER_COLUMN_DENIED/COLUMN_UNKNOWN/ROW_LIMIT_EXCEEDED；注册表 SQL 文本与字面量零漂移由测试强制。契约测试 10 例。**SQL 级谓词下推（引擎权限联动）列入后续** |
| E3-3 持久化执行 MVP | ✅ 已落地（2026-10-30） | PR #27 · squash `7a8ff56` | `durable.py` 步骤级 checkpoint（SQLite 自包含 data/durable.db，cid+请求指纹+步骤唯一）+ /chat 管线接入：context_injection 与 llm_inference 完成即落 checkpoint，同 cid+指纹重入复用产物（LLM 步骤恢复零 vLLM 调用、预算零计费，响应含 resumed_steps）；失败步骤不落 checkpoint（重入自动重执行）。契约测试 7 例 + conftest 全局隔离夹具（防持久库跨运行残留——该污染真实发生并修复）。流式与更多步骤列入后续批次 |
| E3-4 学习闭环落地 | ✅ MVP 已落地（2026-10-30） | PR #34 · squash `b0e56ea` | `learning_loop.py` 三段闭环：usage 回填（token_usage 聚合洞察 /learning/usage-insights）+ golden 候选学习（semantic_query_no_match/blocked 审计事件 → 候选生成与采纳 /learning/golden-candidates·golden-adopt，全量入审计链）+ 指标版本门控（metric_versions 状态表：通过率 ≥0.9 晋升次版本 / 人工回退至历史上一版本，/learning/metric-version·metric-promote·metric-rollback）。契约测试 10 例。附带修复 no-match 路径审计缺失与回滚地板语义 |
| E3-5 规模化预案 | ✅ 预案已预置（2026-10-30） | `deploy/scaling.md` + PR #35 | 路径决策矩阵（DGX 纵向 / K8s+Helm 横向）、Postgres 迁移开关预置（YYC3_DB_BACKEND，非 sqlite 仅 warning 不改存储防未演练切换）、迁移剧本（双写→对账→读写切换→冷备）、MCP stateless 路由说明与状态层三项前置（语义缓存共享化/checkpoint 迁 PG/任务簿共享化）、部署侧验收清单。**实际纵向/横向执行为部署侧决策，未执行** |

> 台账纪律：每项落地 PR 合并后 24h 内更新本表（状态/载体/佐证三列）；跳票须写明原因与新排期。
> **E3 阶段五项全部落地（2026-10-30）✅ 完整收官——E1/E2/E3 三阶段同日交付完毕**。遗留部署侧验收清单（汇总）：① E1-2 judge 一致率**✅ 2026-10-31 实测 87.5% ≥85%（达成，报告入库 evals/reports/judge_consistency_first.json）**；② E1-3 降级演练；③ openai ≥3.39 回归**✅ 2026-10-31 openai 3.42.0 真实调用通过**；④ 兄弟仓跨仓 MCP 联调与第三方 A2A 委托（本机回环已验证，跨网待部署侧）；⑤ E2-3 LongMemEval 100 例实测**✅ 100/100（报告入库）**；⑥ E3-1 正确率 ≥20pct 对照实验；⑦ E3-5 路径执行与迁移演练。

---

> ***YanYuCloudCube***
> *言启象限 | 语枢未来*
> *Words Initiate Quadrants, Language Serves as Core for Future*
> *万象归元于云枢 | 深栈智启新纪元*
