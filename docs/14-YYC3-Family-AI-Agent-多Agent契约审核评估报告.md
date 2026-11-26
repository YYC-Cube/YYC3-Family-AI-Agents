---
file: "14-YYC3-Family-AI-Agent-多Agent契约审核评估报告.md"
description: "基于角色契约（2026-11-26 生效版）多Agent条款的全面多维审核：四件套盘点、契约九锚点代码取证、四层×九层映射、大数据多Agent生态对标，产出 P0/P1/P2 问题明细与 B1-B10 补全建议批次"
author: "YanYuCloudCube Team <admin@0379.email>"
version: "v1.2.0"
created: "2026-11-26"
updated: "2026-11-26"
status: "review"
tags: [多Agent, 架构审核, 四件套, MCP, A2A, 评测基线, 契约, 护栏]
category: governance
language: zh-CN
audience: ai-engineers
complexity: advanced
---

<p align="center">
  <img src="../public/yyc3-family.png" alt="YYC³ Family" width="560">
</p>

# YYC³ FAmily-AI Agent · 多Agent契约审核评估报告

> ***YanYuCloudCube*** · *言启象限 | 语枢未来*
> *审核不是挑错，是把「名」与「实」的对齐成本降到最低。*

---

## 0. 审核定位、方法与数据风险声明

**审核依据**：YYC3 大模型训练/评测/Agent研发指导角色契约（2026-11-26 生效，含补充条款 C1–C6）中的多Agent条款——四层架构（基础层→能力层→决策层→编排层）、模型职责 vs 系统兜底错配识别、评测与架构对齐（工具调用绑定实际 schema/错误码、记忆短/长时区分、规划可达/不可达覆盖）、补充条款 C3 间接注入必测 / C4 端到端预算 / C5 可复现五元组 / C6 小样本置信边界。

**审核对象**：Agent 标准四件套 **Skills / Plugin / MCP / Subagent** 在本仓的落地状态 + 底层代码与架构的契约符合度。

**证据源**（全部只读取证，结论可回溯）：

| 证据族 | 载体 | 规模 |
|---|---|---|
| 四件套盘点 | 双路并行只读检索（盘点的 30 次定位） | 5 项清单全量核实 |
| 契约九锚点取证 | 代码级逐锚点核实（46 次定位） | ①–⑨ 全覆盖，含 call-site 全量核查 |
| 设计文档 | docs/11 v1.1.0（E1/E2/E3 台账）· docs/13 v1.0.0（三路径封装）· docs/20 九层架构 · README / ARCHITECTURE / CHANGELOG | 6 族 |
| 外部核实 | MCP 规范最新版实查（2026-11-26） | 1 项 |
| 对标基线 | 家族 8-Agent 协同闭环技能 + docs/11 §1 生态全景（LangGraph / OpenAI Agents SDK / Google ADK / CrewAI / WrenAI / SuperSonic / DB-GPT / Mem0 / Zep / Letta / OTel GenAI） | 11 项 |

**基准与数据风险声明（契约 C1/C6 落地）**：

1. 本文引用的真机数据（judge 一致率 87.5%、记忆 100/100、语义层对照实验、降级演练 5 场景）均为**自建评测集单轮实测**——属持续更新型自建资产，无公开基准的饱和/污染问题；但样本量小（golden 24 例，远低于 C6 的 N=300 置信边界阈值），结论按**方向性证据**采信，不作为统计显著性结论。
2. 测试总数 331 为本机 `pytest --collect-only` 实测（2026-11-26）；README 徽章「261 passed + 8 skipped」为滞后值（docs/13 W1 台账记 318+8，此后 E3-2 谓词下推等批次又有增量）。
3. 本仓为 Agent 运行时仓；契约「五维驱动」中训练侧两维（Megatron-Bridge / NeMo 对位物）不在本仓范围，按训练集群与兄弟仓口径另行评审，本文不作跨范围结论。

---

## 1. 核心结论（前置）

1. **本仓是「治理强、协同弱」的同构单体集群，尚未构成严格意义的多Agent系统。** 治理面（审计链 / Token 预算窗口 / Kill Switch / 护栏 / MCP 工具面 / 语义层 / 持久化执行）是生态稀缺资产且落地有真机佐证；但多Agent三要素——**真实委托执行、决策层（规划/终止判断）、代理间消息总线**——均未实现：`agent_server.py` 全部出站 HTTP 仅指向治理中枢与 vLLM，**无任何对 25601–25604 兄弟代理端口的调用**；「天枢总指挥」当前是提示词人设 + 治理面阈值建议引擎，`/collaboration` 只产出「建议谁支援」并落审计，不派发、不回收结果。
2. **四件套完成度：MCP ✅（九锚点中最高）、Subagent 部分、Skills/Plugin 仅计划。** MCP server 8 工具 + client 全链闭环（协议 2026-07-28，经外部核实仍为最新正式版）；8 位家人人格文档齐备（24 个 md）但非 ZCode subagent 格式、无真实派发；仓内 0 个 SKILL.md / plugin.json，Plugin（路径 B）按 docs/13 排期 W2 未启动，pip 包骨架（路径 C）已落地。
3. **契约九锚点计分：已实现 2、部分实现 6、完全缺失 1。** 完全缺失项为锚点③（任务规划/分解/终止判断与不可达目标评测）；部分实现中差距最大的三项：间接注入零覆盖（C3 不符）、工具调用评测缺位（覆盖仅在 pytest 不在 evals）、短时/工作记忆零实现（Chroma 为无调用方的孤儿端点，且 hub 19500 vs systemd 8100 段端口矛盾）。
4. **发现「人设职责 vs 系统职责错配」这一契约错配条款的变体**：SYSTEM.md 声明的「全局调度 · 流程编排 · 自愈调度」无代码支撑；沙箱（OpenShell :8080）仅存在于 README/ARCHITECTURE/compose 注释，无服务定义、无调用点。文档-代码漂移共 3 处（另含 ARCHITECTURE 治理中枢端口 :9100 与代码事实 :25700 不符、README「治理工具三件」与实际 8 工具不符），修复成本低但属可信度风险。
5. **评测资产质量良好但未覆盖 Agent 适配主轴**：golden 24 例 + judge（一致率实测 87.5% ≥85% 门槛）、记忆 100 例（100/100）、语义层对照实验（MDL 上下文较裸生成 +10.5pct、危险 SQL 穿透 0）构成真实可信的基线；但全部针对「文本回答质量」，**无工具调用评测层**（契约锚点①），golden 亦无「不可达目标/虚报完成」类目（锚点③）。

**九锚点状态总表**：

| 锚点 | 状态 | 一句话差距 |
|---|---|---|
| ⑨ MCP 工具面 | ✅ 已实现 | 无（8 工具 + schema + 双层错误码 + 审计闭环） |
| ⑧ 治理中枢端口核实 | ✅ 已核实 | 代码事实 25700；ARCHITECTURE :9100 为陈旧错误 |
| ① 工具调用评测 | 🟡 部分 | 覆盖在 pytest 契约测试；evals 无工具调用层 |
| ② 记忆短/长时 | 🟡 部分 | Semantic 层完整+100 例评测；Working 层零实现，Chroma 孤儿端点 |
| ④ 注入检测覆盖面 | 🟡 部分 | 仅用户输入面 + 最终输出；间接注入零覆盖（C3 不符）；流式 delta 不脱敏 |
| ⑤ 系统兜底 vs 模型职责 | 🟡 部分 | 降级/缓存/checkpoint/SQL 门禁完善；无请求内自动重试；沙箱无调用点 |
| ⑥ 延迟与预算度量 | 🟡 部分 | gen_ai.* + 逐调用 latency 有；端到端延迟预算/SLA 无；预算计数器内存态重启清零 |
| ⑦ A2A | 🟡 部分 | 单机最小集闭环；跨网六缺（security 声明/公网 url/任务持久化/异步语义/push notification/TLS） |
| ③ 规划可达/不可达评测 | 🔴 完全缺失 | 无规划/分解/终止判断代码；无不可达目标用例 |

**二审增补（v1.1.0，2026-11-26）**：提示词工程蓝图（docs/10- 全量 44 篇 md + 61 代码文件）深读复核后，一审结论发生四处修订、新增一项契约风险（**提示词诱导执行幻觉**），并确认**「三层资产断层」为本次审核最重要的结构性发现**——详见 §8。九锚点状态总表结论不变（⑨⑧已实现、①②④⑤⑥⑦部分、③缺失），但锚点③的补全路径由「从零设计」修订为「蓝图/原型层迁移+接线」。

---

## 2. 测试/评审维度

### 2.1 契约四层 × 仓库九层映射

契约四层模型对位本仓代码（九层设计见 [docs/20 人机协同·九层架构](./20-YYC3-AI-Family-Agent-编程体系/YYC3-AI-Family-Agent-人机协同/AI-FAmily-Agent-智能协同架构/04-YYC3-AI-FAmily-九层架构设计.md)：基础设施/数据存储/核心服务/AI智能/业务逻辑/应用表现/用户交互/扩展演进/系统设置）：

| 契约层 | 本仓对位物 | 状态 | 证据 |
|---|---|---|---|
| **基础层**（模型推理与工具执行） | vLLM 主备降级 + 语义缓存 + 步骤级 checkpoint | ✅ 系统兜底完善 | `agent_server.py:193-231`（4xx 不切换/5xx 切备援+审计）、`:50-55` 缓存、`durable.py:24-36` |
| | 工具执行链 | 🟡 mcp_client 具备但 agent 管线不消费工具 | `mcp_client.py:86-102`；agent 出站仅 hub+vLLM |
| | 沙箱 | 🔴 仅文档资产，无服务定义与调用点 | `docker-compose.yml:11` 注释 vs services 无此项；`agent_server.py` 全文无 8080 调用 |
| **能力层**（工具编排/RAG/记忆） | RAG 对位物 | 🟡 hub `inject_context`（LIKE 关键词，注释自称「替代简单RAG」）+ Chroma 孤儿端点 | `governance_hub.py:704,1097-1102`；agent 侧不调 `/memory/*` |
| | 长时记忆（Semantic） | ✅ 抽取→去重合并→置信度衰减→审计链 | `memory_semantic.py:25-30,94-106,139-141` |
| | 短时/工作记忆 | 🔴 零实现（`memory_semantic.py:4` 自注「Working/Episodic/Procedural 列入后续批次」） | — |
| **决策层**（规划/反思/终止判断） | — | 🔴 无任何实现 | 全仓 grep 无 plan/decompose/terminate 逻辑 |
| **编排层**（多Agent协作与任务路由） | 协同建议引擎 | 🟡 阈值建议 + 审计留痕，无派发执行 | `governance_hub.py:523-540,556-596`；`agent_server.py:147-158` |
| | A2A | 🟡 单机最小集闭环，跨网六缺 | `agent_server.py:462-542` |

**模型-系统职责划分审计**：系统兜底清单 = 主备降级 / 缓存命中零计费 / checkpoint 断点恢复（重入零 vLLM 调用）/ SQL 校验门禁（11 个结构化错误码）/ 护栏 block 422 / 冻结 403 / 全端点失败结构化错误对象。暴露给模型/调用方侧 = 中危 degrade 放行留痕、上下文注入失败静默跳过（`agent_server.py:143-144`）、全端点失败以 HTTP 200 包 error 对象。**新增错配变体：人设职责 ≠ 系统能力**——8 份 SYSTEM.md 的角色能力声明（尤其天枢调度族）无 per-role 代码分支支撑（`agent_server.py` 对所有家人是同一份通用代码），对外能力表述须与代码事实收敛。

### 2.2 四件套盘点（Skills / Plugin / MCP / Subagent）

| 件套 | 状态 | 事实与证据 |
|---|---|---|
| **Skills** | 🔴 缺失（仅计划） | 仓内无 SKILL.md / skills/ 目录；docs/13 将其排期于路径 B（W2/Step 2），蓝图含 8 人格 skill + commands；A2A Card 的 `skills` 字段（`agent_server.py:474-476`）是能力声明而非 Skill 件套 |
| **Plugin** | 🟡 仅计划（路径 B 未启动）；路径 C 骨架已落地 | 无 plugin.json / .claude-plugin/；蓝图完备（docs/13:97-111,186-199）；pip 包 `yyc3-family-ai 3.1.0`（pyproject.toml:6-28，零依赖 flat py-modules 5 模块 + 三 CLI 入口，wheel 真机构建验证）已落地，src/ 命名空间迁移列后续 |
| **MCP** | ✅ 已落地（服务端 + 客户端） | server 8 工具（governance_budget_overview / governance_audit_search / governance_agent_states / memory_semantic_recall / memory_semantic_store / guardrails_inspect / semantic_query / durable_resume），协议 `MCP_PROTOCOL_VERSION = "2026-07-28"`（governance_hub.py:815），stateless 单 POST 无 session，每次 tools/call 入审计链，kill-switch 刻意不暴露；JSON-RPC 错误码 -32600/-32601/-32602 + 业务结构化错误码；client 四方法 + SSRF 边界 + 双异常。**README.md:90「治理工具三件」为滞后陈述** |
| **Subagent** | 🟡 部分 | 8 目录 × {IDENTITY,SOUL,SYSTEM}.md 齐备但均无 frontmatter（非 ZCode subagent 定义格式）；协同为「建议制」（见 2.1 编排层）；无代理间消息总线，可用回传通道仅审计链 / A2A 内存任务簿（≤200）/ Agent Card |

**仓外部署侧资产对照（本会话环境观察，未逐项核验，不计入仓内完成度）**：本会话的 ZCode 环境中存在 `yyc3-family` MCP 面（40+ 工具，含 shared_*/tianshu_*/guardian_* 等本仓 governance_hub 未有的工具）、yyc3-* 用户级技能、8 位家人 subagent 类型——提示 W2 Plugin 封装可复用既有部署侧资产；建议列入对账清单（见 B10）。

### 2.3 契约九锚点状态

见 §1 总表。锚点级证据要点：

- **锚点①（工具调用评测）**：evals/ 仅评测 `/chat` 文本回答（`run_evals.py:103`），全目录无 tools/call、jsonrpc、-32602 相关用例；MCP schema 与错误码覆盖存在于 `tests/integration/test_mcp_server.py:33-39,77-91,108-111`（8 工具名 + inputSchema type + 四错误码路径 + 缺参 -32602）。pytest 契约测试 ≠ 评测资产：无「按 tools/list 实际 schema 驱动生成用例」机制。
- **锚点②（记忆）**：Semantic 层 100 例七类（basic 30/interference 20/isolation 15/merge 10/forget 10/decay 10/leak 5）100/100（`evals/reports/memory_eval_final.json`）；短时上下文实际来源是 hub 图谱注入（非记忆系统）；Chroma 端口 hub 侧 19500（`governance_hub.py:1101`）vs systemd `yyc3-memory.service` 8102，且 compose 无该服务。
- **锚点③（规划评测）**：golden 类目校验仅 `identity/domain/boundary`（`golden_cases.json:34`）；boundary 测拒答而非虚报完成；无持续无效调用检测。
- **锚点④（护栏覆盖面）**：13 条正则（`guardrails.py:19-33`，high 9 类 block / medium 3 类 degrade）；call-site 全量核查仅 4 处：/chat 用户消息（:319）、流式用户消息（:565）、非流式最终输出脱敏（:424）、MCP 显式检视工具（hub :906）。**未覆盖**：hub 图谱注入内容（:356-362 直拼 system prompt）、history、A2A message.parts（:502-506）、工具返回、**流式 delta 输出不脱敏**。9 类注入样本拦截 100%、误杀 0/6（自建样本集，门槛 95%/2%）。
- **锚点⑤（兜底 vs 模型）**：checkpoint 指纹不含 cid（`durable.py:48-51`，同指纹跨 cid 复用）；失败步骤不落 checkpoint 重入自动重执行；无请求内自动重试（`call_vllm` 单遍历端点列表）；「重试」仅存在于跨请求重入语义与部署侧 evals。
- **锚点⑥（度量）**：`genai_attrs()` 对齐 semantic-conventions-genai Development 子集（`telemetry.py:61-71`）；latency 记录四点（token_usage.latency_ms / /budget/history / usage_insights AVG / 响应体）；grep 无 latency_budget/p95/SLA。预算窗口日/周/月惰性重置（hub :436-467）+ degrade 80%/85% / block 100% 阈值（:484-485），但 `_budgets` 为内存 dataclass（:394-404），**hub 重启计数清零**（明细 token_usage 已入库，聚合态未落库）。
- **锚点⑦（A2A）**：Card 字段齐但无 `security`/`securitySchemes`，url 写死 `localhost:{PORT 默认 6000}`（`agent_server.py:468`）；message/send 同步阻塞无异步 task 语义；任务簿进程内存 ≤200 重启丢。
- **锚点⑧（端口）**：代码/compose/systemd/README 五处一致 25700（`governance_hub.py:1640-1641`、compose :51/:57/:78/:115）；ARCHITECTURE.md:15/:73 的 9100 为陈旧错误（同文档 ADR-03 亦自相矛盾）。

### 2.4 多Agent核心技术对标

**生态对标更新（对 docs/11 §2 差距表的 2026-11-26 复核）**：

| 生产维度 | docs/11 基线评级 | 本次复核 | 复核依据 |
|---|---|---|---|
| 流式输出 | 🔴 | ✅（E1-1 收官） | /chat/stream + 契约测试 |
| 持久化执行 | 🔴 P0 | ✅（E3-3 收官 + 流式 checkpoint） | durable.py + 2026-11-24 批次 |
| 评估基线 | 🔴 | ✅（golden+judge 双轨）+ **新增缺口：工具调用层** | §2.3 锚点①③ |
| 记忆 | 🔴 | 🟡（Semantic ✅ / Working 🔴 / Chroma 孤儿） | §2.1 能力层 |
| 工具协议 MCP | 🟡 | 🟢（server 8 工具 + client；协议版本经外部核实未过时） | §2.2 |
| A2A | 🟢（结构备） | 🟡（单机闭环，跨网六缺） | §2.3 锚点⑦ |
| 可观测 | 🟡 | 🟢（gen_ai.* 已挂载）/ 🟡（agent spans 编排段无对象可挂——编排未实现） | §2.3 锚点⑥ |
| 治理/预算/审计 | 🟢 独有优势 | 🟢 + 新披露：预算聚合态内存态 | §2.3 锚点⑥ |
| 编排模型 | 🟡 固定链缺动态编排 | 🔴→🟡 修正：不是「固定链」而是**建议链**——委托无执行者 | §1 结论 1 |
| 沙箱 | —（未单列） | 🔴 新列：文档资产非代码资产 | §2.1 基础层 |

**协议外部核实（2026-11-26）**：MCP 最新正式版仍为 **2026-07-28**（draft changelog 累积小改，下一版路线 2027-03-30）——本仓「对齐 2026-07-28 stateless 子集」为当前版本，无升级压力；A2A 状态依 docs/11 调研（Linux 基金会 v1.0，渗透早期），本仓跨网缺口与生态渗透节奏匹配，不构成落后。

**家族协同闭环对标（yyc3-ai-family-coding 技能 ①→⑥ 环 vs 代码事实）**：①入口唯一（千行路由）→ 代码未特殊化（同构 agent_server，无路由分支）；②编排唯一（天枢）→ 建议制半环；③并行专业执行 → 无派发；④交叉审核（宗师×守护×天枢）→ 无代码实现（相关工具在仓外 MCP 面）；⑤聚合交付 → 各代理独立响应；⑥反馈回流 → ✅ learning_loop 三段闭环（usage 回填 / golden 候选 / 指标版本门控）为**唯一全环落地的协同环节**。六环计约 1.5 环落地。

---

## 3. 核心数据指标

| 指标 | 数值 | 来源与局限 |
|---|---|---|
| 测试用例总数 | 331 collected（含 8 门控 skip） | 本机 `pytest --collect-only` 2026-11-26 实测；CI pytest 全量门禁 |
| MCP 工具面 | 8 工具 / 协议 2026-07-28 / JSON-RPC 错误码 3 种 + 业务结构化错误码 11 种（semantic_layer 全集） | governance_hub.py:817-860；semantic_layer.py 错误码定位 |
| golden 评估 | 24 例（identity/domain/boundary 8×3）；规则通过率 91.7%；judge 一致率 87.5%（门槛 ≥85%） | evals/reports/judge_consistency_first.json；单轮实测，N<300 按 C6 只作方向性证据 |
| 记忆评测 | 100 例七类 100/100（门槛 0.9） | evals/reports/memory_eval_final.json；仅覆盖 Semantic 层 |
| 语义层对照实验 | 确定性路由 100%（19/19）· MDL 上下文 LLM 94.7% · 裸生成 89.5%（+10.5pct）；危险 SQL 穿透 0；治理面外误匹配 6/7（match_metric 无阈值设计） | evals/reports/semantic_accuracy_first.json；2 表演示域 + 强基线模型，20pct 门槛须生产级多表域复测 |
| 降级演练 | 5 场景全 PASS（含流式兜底合成） | evals/reports/e13_failover_drill_real.json |
| PG 迁移演练 | 阶段 1 全对（6 表行数+SHA-256 对账、审计零断链）；阶段 2/3/4 待 hub PG 数据层 | evals/reports/e35_migration_drill_real.json |
| 护栏 | 13 条正则；9 类注入样本拦截 100%、误杀 0/6（门槛 95% / ≤2%，自建样本集）；覆盖面 4 个 call-site | test_guardrails.py:31-100 + call-site 全量核查 |
| 预算 | 8 家人 × 日/周/月限额（如 tianshu 日 50 万 token）；degrade 80%/85%、block 100%；聚合态内存态 | governance_hub.py:358-367,484-485,394-404 |
| A2A | 单机最小集（Card + message/send + tasks/get）；任务簿内存 ≤200；错误码 -32600/-32601/-32001/202 | agent_server.py:457-542 |
| 文档-代码漂移 | 3 处（ARCHITECTURE 端口 9100、沙箱 8080 调用声明、README MCP「三件」+徽章 261+8） | 逐条 file:line 见 §2.3 |
| 协同闭环落地 | 六环约 1.5 环（⑥学习回流全环 + ②编排建议半环） | §2.4 |

---

## 4. 问题明细（P0 阻断 / P1 必修 / P2 建议）

**P0（不补则「多Agent系统」名实不副，且为契约编排层/决策层评审阻断项）**

| # | 问题 | 契约条款映射 |
|---|---|---|
| P0-1 | 编排层空转：协同为建议制，无真实委托派发与结果回传；fallback 链无执行者 | 四层·编排层；职责错配条款 |
| P0-2 | 决策层整体缺失：无任务规划/分解/终止判断；不可达目标评测零覆盖（持续无效调用/虚报完成均无检测） | 锚点③；MCPHallu 三轴 |
| P0-3 | 工具执行链断裂 + 沙箱缺位：agent 管线不消费 MCP 工具；OpenShell 沙箱无服务定义无调用点，仅存文档声明 | 四层·基础层；五维驱动沙箱维度 |

**P1（3 个月内，契约补充条款与评测主轴）**

| # | 问题 | 契约条款映射 |
|---|---|---|
| P1-1 | 间接注入零覆盖：图谱注入内容/history/A2A parts/工具返回不经检测；流式 delta 不脱敏 | **C3 必测条款不符** |
| P1-2 | 工具调用评测层缺位：evals 无 MCP 工具调用 golden；无按实际 schema 驱动用例的机制 | 锚点①；评测-架构对齐条款 |
| P1-3 | 短时/工作记忆零实现；Chroma 孤儿端点 + 端口矛盾（19500 vs 8102）；评测不覆盖向量链路 | 锚点②；记忆短/长时区分条款 |
| P1-4 | 端到端延迟预算缺失（仅逐调用 latency 记录，无预算阈值/p95/告警）；Token 预算聚合态内存态重启清零 | **C4 不符**；E3-5 状态层前置 |
| P1-5 | 跨网 A2A 六缺（security 声明/公网 url/任务持久化/异步语义/push notification/TLS）——docs/11 遗留④ | A2A 互操作 |
| P1-6 | 四件套 Skills/Plugin 未落地（W2 排期进行中，需与仓外部署侧资产对账后封装） | 四件套标准 |
| P1-7 | golden 规模 24 例低于 E1-2 自设 50-100 例目标，低于 C6 N=300 置信边界；且无「不可达目标」类目 | C6；锚点③ |

**P2（建议）**

| # | 问题 |
|---|---|
| P2-1 | 文档-代码漂移 3 处（ARCHITECTURE :9100、沙箱声明、README 三件+徽章滞后）；CI docs-links 不查代码事实类漂移 |
| P2-2 | match_metric 无阈值误匹配（docs/11 已列：治理面外 6/7 长尾误答 total_users）→ 意图分类+阈值升级 |
| P2-3 | 根目录 examples/ 为 PR#61 迁移残留（untracked 74 文件，其中 3 个测试脚本目录引用为改名前旧值），CI 仅检查 docs 版 |
| P2-4 | agent 管线无请求内自动重试（当前依赖跨请求重入语义；对 LLM 网关类瞬态故障无单请求兜底） |
| P2-5 | 8 位家人人格文档无 frontmatter，与 ZCode subagent/Plugin skills 格式不对齐（影响 W2 封装效率） |

---

## 5. 根因分析

按契约三分法（数据/训练策略/架构适配）适配到系统评审，本轮根因落在**架构适配与演进时序**两域，无数据域问题（评测集质量经 judge 一致率与真机实验佐证）：

1. **编排/决策缺失 = 演进时序未至，非能力上限。** ADR-01（单模型 + 治理中枢集中式）把资源优先投向治理面这一差异化护城河（docs/11 北极星 4），E1/E2/E3 三阶段按「先补课后赶新」纪律执行——编排真实化被合理后置。但由此产生**人设职责 vs 系统职责错配**：SYSTEM.md 与 README 的能力表述走在了代码前面。根因不是「做不了」，是「声明了未实现」。修正路径有二：实现（B3/B4）或收敛声明（B1）——二选一必须发生，否则下游消费者按声明集成将失败。
2. **评测断层 = 两波建设未合流。** evals 体系建于 E1-2（评 /chat 文本质量），MCP 工具面建于 E2-2/W1（协议工具）——两者相隔一个阶段且接口形态不同（HTTP /chat vs JSON-RPC tools/call），evals runner 未随之扩展。属时序断层，补 B6 即可，无须重构 evals 骨架（规则断言引擎 `evaluate_rules()` 与报告结构可复用）。
3. **沙箱空缺 = 蓝图资产与产线管线错配。** OpenShell 在 examples 蓝图层（1306 协议栈/1307 安全合规）有原型，产线 agent 管线从未接线；docs/11 §2 安全行「无注入护栏与执行沙箱」的差距评级在 E2-4 护栏落地后未同步收敛沙箱半边。
4. **文档漂移 = 账本纪律覆盖面不足。** docs/11 §9 台账纪律（24h 内更新）只约束演进规划文档本身；README/ARCHITECTURE 无「代码事实对齐」机制，CI docs-links 仅查存在性/旧称/死链，不查端口、组件清单、工具数等代码事实。漂移不是错误而是缺检查器。
5. **记忆半成品 = 分层设计的刻意分期**（`memory_semantic.py:4` 明示 Working/Episodic/Procedural 列入后续批次）——但 Chroma 端口矛盾与孤儿端点属**分期遗留未收口**：P0-3 记忆路由建设时向量侧未同步接线或降级声明。

---

## 6. 优化建议（B1–B10 批次，附适用/不适用条件）

> 排序原则：先收口可信度（B1 快赢），再补契约阻断项（B2–B4），再契约条款与评测主轴（B5–B8），最后部署侧依赖项（B9–B10）。每项遵循 docs/11 §6 生产落地检查清单（评估/回滚/观测/预算/安全/审计/文档七勾）。

| 批次 | 内容 | 方案要点 | 适用条件 | 不适用条件 | 退出标准 |
|---|---|---|---|---|---|
| **B1** 文档可信度收口（P2-1/P2-3，先行快赢） | 修 ARCHITECTURE 端口 :9100→:25700；沙箱声明改为「规划中」或接线后恢复；README「三件」→「八件」+徽章数字刷新（以 CI 实跑为准）；确认删除根 examples/ 残留 | 全部为文档/残留操作 | 立即适用，零运行时风险 | — | CI 绿；`grep -rn "9100" ARCHITECTURE.md` 零命中；`git status` 无 examples/ 残留 |
| **B2** CI 防漂移门禁（P2-1 根治） | docs-links job 增加代码事实断言：治理中枢端口数（grep 25700）、MCP 工具数（pytest 断言 tools/list 长度已有，补「README 工具清单与 MCP_TOOLS 对齐」静态检查）、沙箱调用点存在性或「规划中」标记检查 | 复用既有 docs-links 模式 | 与 B1 同批 | 不宜过度断言（只锁高价值事实项） | CI 新检查项红→绿各演练一次 |
| **B3** 编排层真实化 MVP（P0-1） | `_check_collaboration` 建议结果升级为可执行委托：agent_server 增加兄弟端点 HTTP 委托（env 化，复用 GOVERNANCE_ENDPOINT 同款模式）+ 委托深度上限（防循环委托，建议 ≤2 跳）+ 预算按委托链扣减 + 结果回传写审计链；任务簿迁 SQLite（复用 durable 表模式） | 单机内 8 端点互达；须先有 B4 的终止判断防无限委托 | 遵循 docs/11 反模式纪律：不引框架整体重写，吸收 checkpoint 语义 | 跨网场景不适用（走 B9） | 天枢一次真实委托→兄弟代理执行→结果回传→审计链连续；强制深度上限演练 |
| **B4** 决策层最小实现 + 不可达目标评测（P0-2） | 天枢侧任务卡结构化（workflow 模式：分解→派发→终止条件，参照 Anthropic 五模式「按需选型」纪律）；golden 增设 `unreachable_goal` 类目：断言「不可达目标下调用次数上限 + 虚报完成话术 must_not_include + 如实报告失败 must_include_any」；评测范式参照契约 MCPHallu 三轴（推理/执行/记忆幻觉分账） | 依赖 B3 派发通道；评测类目可先行（不依赖派发，可先评 /chat 承诺一致性） | 不可达目标评测先行落地 | 不做通用规划器（反模式：过度 Agent 化） | unreachable 类用例入 golden 且规则引擎可判；虚报完成检测有正反例 |
| **B5** 间接注入护栏扩展（P1-1，C3 收口） | guardrails 检视面扩至：hub 图谱注入内容（`_inject_context` 返回值）、history 尾部窗口、A2A parts、（B3 后）委托返回内容；流式 delta 脱敏策略（按事件边界在 delta 侧检测 + done 前聚合校验，须与「单 delta 重放」兼容）；样本集增设「间接注入」类目（检索内容/工具返回形态），保持拦截率 ≥95%、误杀 ≤2% 双门槛 | 注意误杀风险：审计记录/文档原文可能天然含「忽略之前指令」类触发词，须建误杀探针回归 | 与 NemoClaw 沙箱策略联动验证（模型侧拒答与沙箱侧拦截分别测、不互相替代——契约 C3 原文） | 不做重型分类器 MVP（docstring 已自认规则 MVP 先行，分类器列后续） | 间接注入样本集拦截 ≥95%、误杀 ≤2%；流式与缓存重放路径脱敏测试绿 |
| **B6** 工具调用评测层（P1-2，锚点① + C5） | evals 新增 `run_tool_eval.py`：用例从 `/mcp` tools.list **实际 schema 生成**（契约「绑定实际 schema」正解）；断言四层——JSON-RPC 错误码路径 + 业务结构化错误码（semantic_layer 11 码全集抽样）+ 审计链写入验证 + latency 记录；报告带 C5 五元组（commit hash / 数据集版本 / 框架版本 / 解码参数 / 协议快照日期 2026-07-28） | 复用 run_evals 报告结构与 --min-pass 退出码模式 | 公开基准（BFCL 等）以范式参照为主，不直接套跑（协议不同；采纳其「多轮+状态比对」思想自建） | — | 工具调用 golden ≥30 例入 evals；CI 挂软门禁；报告含五元组 |
| **B7** 记忆体系收口（P1-3，锚点②） | 三选一并明示：① Chroma 接线 /chat 上下文组装（RAG 主链路补全）；② Chroma 降级为 P2 并从 README 特性表移除；③ 以 Semantic 层承担记忆并归一端口（19500/8102 二选一）；`memory_semantic.py` 显式命名 Working 层边界（docstring 已留口） | 需部署侧先定 Chroma 服务形态 | 与 E3-5 状态层前置（语义缓存共享化/checkpoint 迁 PG）统筹 | — | 端口单一事实源；记忆评测覆盖所选链路；README 表述与决策一致 |
| **B8** 预算持久化 + 端到端延迟预算（P1-4，C4） | 预算聚合态落库（随 E3-5 阶段 2/3/4 hub PG 数据层一并做，避免双写过渡态）；telemetry 增 latency histogram + 端点级 p95；预算模型加延迟维度（E1-1 已有「首字延迟 <2s」退出标准可直接复用为阈值） | 依赖部署侧 PG 落地节奏；p95 需最小样本量 | OTel GenAI 处 Development 状态——对齐方向不锁死细节（docs/11 北极星 5） | — | hub 重启预算不清零；p95 入五支柱面板；延迟阈值触发行为（降级/告警）有审计 |
| **B9** 跨网 A2A（P1-5，docs/11 遗留④） | Card 补 `security`/`securitySchemes` 声明（对齐 A2A v1.0）；url 由部署侧注入；任务簿持久化（依赖 B3 迁库）；异步 task 语义（提交→轮询/SSE）；TLS/反代方案入 deploy/ | 有跨网部署需求时优先 | 单机内无影响，不阻塞其他批次 | docs/11 判断「渗透早期」——不自建注册中心，跟规范走 | 第三方 A2A 客户端跨网发现→委托→追溯全链（E2-5 退出标准的跨网版） |
| **B10** 四件套收口（P1-6/P2-5） | W2 路径 B 落地 `.claude-plugin/`（plugin.json + 8 人格 skills + commands audit/budget/freeze + guardrails hook + .mcp.json）；封装前先对账仓外部署侧资产（用户级 MCP 面 40+ 工具 / yyc3-* 技能 / 家人 subagent 类型），能复用则迁入不重写；人格文档 frontmatter 化；遵守「万能插件」反模式（按职能拆分） | docs/13 W2 排期内；对账清单先行 | ZCode/Claude Code 生态格式以官方 spec 为准，不自研格式 | — | `/plugin add` 一行安装可用；npm pack 清单正确；与仓外资产对账表入 docs/13 |

**执行顺序建议**：B1+B2（同批，1 个 PR）→ B6+B4 评测侧（可先行，不依赖派发通道）→ B3+B5（编排与护栏联动）→ B7/B8/B10（按部署侧节奏）→ B9（最后）。

---

## 7. 预期效果与风险提示

**预期效果**：

- B1/B2 落地后，文档-代码漂移类问题获得机制性防护，可信度风险清零（本审核 P2-1/P2-3 关闭）。
- B3/B4 落地后，契约四层模型四层齐备，「多Agent系统」从声明变为代码事实；不可达目标评测使「虚报完成」从不可检变为门禁可判——这是契约锚点③从完全缺失到可评测的最短路径。
- B5/B6 落地后，契约 C3（间接注入必测）与锚点①（工具调用评测绑定实际 schema/错误码）收口，评测体系从「文本质量单轴」扩展为「文本 + 工具调用」双轴，且报告自带 C5 五元组可复现。
- 全批次落地后，九锚点预期态：已实现 2→7、部分 6→2、缺失 1→0（余下部分项为 B9 跨网要素与 B7 Working 层，均受部署侧依赖约束）。

**风险提示**：

1. **B3/B4 为本报告风险量级最高项**：委托链引入新失败面（超时/循环委托/部分失败）。缓解已内置（深度上限 ≤2 跳、预算按链扣减、终止判断先行、审计连续性断言）。**B4 的不可达目标评测必须先于 B3 全量开闸**——先有「虚报完成检测」，再放真实委托，防错配以更大规模重现。
2. **B5 误杀风险**：间接注入检测面扩大后，含指令性措辞的合法内容（审计记录、模板文本）可能被误拦，直接侵蚀「审计链可回放」卖点。缓解：误杀探针随样本集同步扩充，双门槛（拦截率/误杀率）同测，任何一侧破线即回退规则集。
3. **提示词层变更的对齐税提示**：若为收敛人设声明而修改 SYSTEM.md（B1 的替代路径或 B4 配套），属提示词变更——须走 P2-2 模板版本化下发 + golden 身份类用例回归，防人设漂移（P2-4 UAT 既有门控）。本仓不涉模型微调，无经典对齐税。
4. **依赖约束如实声明**：B7/B8/B9 受部署侧（Chroma 形态、PG 数据层、跨网环境）制约，仓内可完成结构件与评测件，退出标准中的部署侧验收项不因本报告而提前承诺。
5. **数据局限重申（C6）**：本报告全部实测数据为单轮自建集结果，批次退出标准的门槛值（95%/2%/0.9 等）沿用仓内既定标准；扩大样本量至 N≥300 并加置信区间，列入 golden 扩容（P1-7）的验收条件。

---

## 8. 二次审核（v1.1.0 增补）：提示词工程蓝图（docs/10-）全量深读复核

### 8.1 范围与方法增补

二审在一审基础上全量深读 `docs/10-YYC3-提示词工程-企业蓝图/`：**44 篇 md（约 9,400 行）+ 61 个代码文件**。分工：1200/1206/1207/1208/1209/1210–1214 直读（含治理层四篇关键词级快扫）+ 两路并行探查（1201–1205 实战文档 30 篇 9,489 行逐篇读毕；13- 代码族 61 文件 60 次定位）+ 两项补充验证（审计链哈希 grep、`agents/` 目录名核实）。全部结论附 file:line，方法与一审相同。

### 8.2 结构性结论：三层资产断层（本审核最重要新增）

| 层 | 载体 | 形态 | 事实 |
|---|---|---|---|
| **蓝图设计层** | docs/10-/12-（1200–1214，41 篇） | 成文 2026-06-03，设计对象为**兄弟仓形态**：全 TS 路径 `src/app/lib/*.ts`（1214:38-85）、模型 GLM-6/Qwen-4.0/DeepSeek-V3（120101:90）、独立 MCP/A2A Gateway 30800-30804（1213:242-243、1212:179-180）、K8s/vitest 部署（1214 §七） | 本仓产线成文时不存在；产线落地后从未回写 |
| **原型层** | docs/10-/13-（1300–1308，61 文件） | **零 LLM、零出站 HTTP 的确定性规则引擎**（全族 grep requests/urllib/httpx 零命中）；端口叙事同构（6000-6007↔25600-25607，docker-compose-all-agents.yml:29-213），行为契约不同构（零治理上报、零互调）——「平行教学宇宙」，不是产线的早期版本 | 27 个文件 sys.path/挂载指向旧族名（`06-协议栈`/`07-安全合规`/`00-核心基础设施`）→ ImportError 全量回退 None；compose 6 个网关为死服务（跑客户端/库且无 server，启动即退出） |
| **产线层** | 仓库根目录 | Python/Flask 治理+LLM 全管线（hub 25700 / agent 25600-25607 / vLLM 8000） | E1/E2/E3 落地，与上两层无映射机制 |

**断层证据四条**：① 1207 §4.2 / 1208 §七 / 1209 §七 三张对齐表全部过期且指向兄弟仓 TS 路径（产线已实现的零信任/guardrails/OTel 在蓝图仍标「规划中」）；② 1200 §七 Phase 勾选**双向漂移**（「建立 ReAct-C 协同工作流框架 [x]」无代码支撑；MCP/A2A/OTel 已落地却未勾）；③ `API_DOCUMENTATION_V3.md:998-1005`「通过率 100% · A+ · Production Ready」判词与本族 README:37 自认「full_suite 尚余 31 例内容性脱节」矛盾；④ docs/13 §1.3「审计链（FNV-1a 链式哈希，防篡改）——极稀缺」卖点与代码不符（`governance_hub.py` 仅 2 处 sha256 用于模板下发内容指纹 :1600/:1622，无链式 prev_hash；该资产是否属兄弟仓 kernel 待验证）。

**影响**：三层不可互查 → 本二审 6 个「名实不符」新发现全部源于此；新会话/新成员极易把蓝图叙事或原型结构当作产线能力。

### 8.3 蓝图域新发现明细

**A. 「提示词工程」名实（1200/1201-1205/1300）**

| 发现 | 证据 | 影响 |
|---|---|---|
| 44 篇文档中可直接下发的提示词模板仅 **4 篇 5 个**（120101×2 / 120102×1 / 120103×1 / 120401×1），其余为方法论+伪代码；占位符 `{{ }}` 仅 4 篇且风格不一（120101:146-154 双花括号包 JSON 疑转义残留） | 探查逐篇统计 | 「提示词工程」实质含量与文档体量严重不匹配；W2 Skills 封装的模板素材远比目录体量显示的少 |
| **1200 §八-B 模板库人格错位**：千行=「代码与架构专家」、万物=「内容与创意专家」、宗师=「知识管理与检索专家」，与同文档主矩阵（§2.3 千行=导航员）及产线 IDENTITY（导航员/思考者/质量官）三方冲突 | 1200:813-831 vs 1200:294-326 vs agents/*/IDENTITY.md | 若按八-B 封装 Skills/W2 将人格错乱；疑似自兄弟仓语境复制 |
| **提示词诱导执行幻觉**（契约 MCPHallu 执行轴新风险项）：天枢模板直接指示「调用预见先知获取趋势预测」（1200:162-165），八-B 模板要求输出 `agents_involved/execution_plan` JSON（1200:803-810），产线无任何调用通道 | 1200 vs agent_server.py 出站面 | 模型遵从提示词即虚报调用——SYSTEM.md 若继承该叙事，golden boundary 类用例应增「虚报调用」断言 |
| 1300 `prompt_engine.py` 类注释宣称「版本控制与回滚、A/B 测试」（:189-190），代码无实现；`{var}` 渲染为顺序 replace、非递归无转义、未填变量原样残留（:491-512） | prompt_engine.py | 蓝图层「夸大宣称」又一例；渲染器迁移须换参数化方案并对缺变量报错 |

**B. 契约域强化证据**

| 契约条款 | 二审证据 | 结论修订 |
|---|---|---|
| **C3 间接注入必测** | 规格三处现成：1209 §4.1 八类攻击分类学（间接/编码/多轮/上下文劫持/角色扮演/工具调用注入）；1214 §6.1 InjectionDetector 契约（`detect(input, {history, systemPrompt})` 签名已含上下文检测面）；**1307 原型已有可迁移正则**——indirect_injection / encoding_injection / context_hijacking / multilingual_injection / tool_injection 五组（content_filter.py:397-431，其中 :410 一条正则字符类嵌套病态须修）+ 输出 PII 脱敏四类（身份证/手机号/银行卡，:118-123,383-389——产线 `redact_output` 仅凭据形态） | B5 由「新设计」修订为「**迁移+分级映射**」（indirect→medium:degrade、context_hijacking→high:block） |
| **C4 端到端预算** | 1208 §3.1-3.3 完整 SLO/SLI/SLA + 错误预算（latency p50/p95/p99 Histogram + P95≤2s SLA + 幻觉率 ≤3% 告警阈值 + 决策准确率 ≥90% + 四级预算消耗告警）+ trace 属性设计（`mcp.server/mcp.tool/a2a.from/a2a.to`，1208 §4.2）；1308 原型 `calculate_slo_compliance`（:352-367）可复用 | B8 由「新设计」修订为「**迁移+适配**」；幻觉率/决策准确率指标为契约六维幻觉诊断提供落点 |
| **锚点③ 规划** | 蓝图/原型层计划级设计丰富：ytianshu `_decompose_task`+`_schedule_agents` 产出编排 JSON（子任务/优先级/并行分组/deadline，ytianshu_agent.py:238-317）但**永不 POST**；yanqi 能力矩阵+fallback 链（yanqi_agent.py:73-122）；1306 A2AClient 契约含 sendTask/onStateChange/cancelTask + SSE 状态流（a2a_client.py:225-332）；1207 §3.4 委托流程 + 1214 §四契约 | 一审「完全缺失」修订为「**产线执行层缺失、设计资产充裕**」——B3/B4 补全路径=迁移+接线 |
| **微调域溯源（C2/C5，待验证）** | 1213:27 记录 N2 DPO 偏好对齐训练（2026-06-04 预期完成）；120503:191-231 声明 LoRA/NeMo AutoModel 微调与 pgvector/AIStore 栈 | 产线 README 仅写模型名 Qwen3.6-27B-FP8，**模型与 DPO checkpoint 血缘未在仓内记录**；按契约 C2/C5 应在模型资产清单补 checkpoint 溯源（属训练设备侧动作，本仓列为待验证项） |
| **1201-1205 技术声明对齐率** | 十二项技术性声明（模型/端点/协议/委托/自愈执行）中仅 **1 项**（Qwen3-Embedding-8B，120503:218）与产线对齐；GLM-6/Qwen-4.0 未见公开版本记录（按契约 C1 标注待验证）；`gpt-4-turbo`/`text-embedding-3-large`/Pinecone 声明与「本地推理」定位相悖（120105:151,155 / 120204:121-123） | 蓝图模型/栈声明不可作为产线依据；下发前须清洗（探查可落地清单第 4 条） |

**C. 原型层迁移评估（对应产线缺口）**

可迁移：① 委托编排数据结构（ytianshu 分解/yanqi 矩阵/1306 A2A 契约与 12 条通信矩阵 :460-475）→ B3；② 1307 注入正则五组 + PII 脱敏 → B5；③ 1300 PromptTemplate 元数据 schema（template_id/version/scene/variables，:54-66）+ 8 家人模板清单（ai_family_prompt_templates.py:169-328）→ P2-2/W2 Skills 数据源；④ 1308 SLO 计算 + 17 字段日志脱敏表 → B8；⑤ 1306 mcp_client 的 prompts/resources 域与指数退避（:274-337）→ 产线 client 增强（保留产线独有 SSRF 边界）。
判死端（评审判断，采纳权在用户）：1301 torchrun/NeMo 双机方案（产线为 vLLM+备援端点）；1308 自造 Span 协议（X-Trace-ID vs 产线 W3C traceparent+OTel）；17 个业务 v2 引擎的「AIFamilyCoordinator 协同」（静态角色描述拼 JSON，无 LLM 无互调）；6 个伪网关服务与 `yyc3-secret-{agent_id}` 弱密钥派生模式。

**D. 质量缺陷清单（P2 级，修复成本低）**

27 文件旧族名死引用（sys.path/compose 挂载，含不存在的 `prometheus.yml`）；6 死网关服务；约 30 处悬空引用（1105/1106 系列文档不存在）；25 篇 frontmatter `file:` 保留旧编号 1108xxxx 全量未改 + 120504/120503 ID 重复 + 120501/120502 维度字母互换（知/学）；120104:340-341「AIOps L2/L3 ✅已实现」与 120504:313-314「留痕100%不可篡改」超前宣称；伪代码硬伤 3 处（120405:128-131 `'service_level': 99%` 非法语法等）；`standardization_api_v2.py:199` `debug=True`、`docker-compose-full-stack.yml:82` redis 默认弱密码回退；`zhiyu-bole` 目录名以拼音残留旧称「知遇」（CI 门禁仅查中文形态，绕过）；CI 守卫缺口：不查旧族名死引用（27 文件漏网根因）。安全面整体干净：61 文件无硬编码密钥、无 MD5、无 SQL 执行。

### 8.4 一审结论修订表

| 一审条目 | 二审修订 |
|---|---|
| 锚点③「完全缺失」 | 修订为「产线执行层缺失、蓝图/原型设计资产充裕」——补全路径=迁移+接线，非从零设计 |
| 「文档-代码漂移 3 处」 | 扩展为**系统性双向漂移**：蓝图层未回写（3 张对齐表+Phase 勾选）+ 产线卖点夸大（FNV-1a 审计链）+ 原型层 27 死引用/判词矛盾 |
| P0-3 沙箱/护栏缺口 | 原型层 zero_trust_gateway/content_filter 有库级实现（含注入五组正则、PII 脱敏、四认证、限流）——P0-3 修订为「**接线决策**」而非「从零建设」；注意弱密钥模式不回迁 |
| P2-3 examples/ 残留 | 不变；补充：docs 版 3 个测试套件 sys.path 已修（full_suite:24-35），仅 `smart_suite.py:121` 残留 1 处冗余死 insert |
| B5/B8 素材来源 | 由「新设计」修订为「迁移+适配」（见 8.3B） |
| 新增 | P1-8 提示词诱导执行幻觉风险（golden 需增「虚报调用」断言类目）；P2-6 蓝图层回写与三层映射缺失（结构性，见 B11） |

### 8.5 补全建议增补（B11–B13；B1/B2/B5/B8 素材落点更新）

| 批次 | 内容 | 方案要点 | 适用/不适用 | 退出标准 |
|---|---|---|---|---|
| **B11** 蓝图层回写与三层映射（P2-6，建议与 B1 同批——名实不符的根，成本低） | 1207/1208/1209 对齐表回写为本仓 Python 产线事实（或标注「兄弟仓形态，另见本仓对齐」）；1200 Phase 勾选校正 + §八-B 模板人格修正或标注废弃；API_DOCUMENTATION_V3 加历史声明（去 Production Ready 判词）；docs/13 §1.3 FNV-1a 卖点修正（待验证归属后改述）；docs/10 分区 README 增「蓝图↔原型↔产线」映射索引 | 涉及提示词/对外表述的变更走模板版本化+golden 回归 | 不重写蓝图方法论正文（其设计价值保留） | 三张对齐表与产线一致；映射索引可从任一层查到另两层 |
| **B12** 原型层死引用/死服务清理 + CI 守卫扩展（并入 B1/B2） | 27 文件 sys.path/挂载改 1300 族名或标注示例弃用；6 死网关服务删除或改注记；`debug=True`、redis 弱密码回退、smart_suite:121 死 insert 清理；CI docs-links 增旧族名守卫（`00-核心基础设施`/`06-协议栈` 等）；~~拼音旧称守卫（`zhiyu`）~~ **执行期勘误：`zhiyu_bole` 为产线在用标识符（hub/compose/tests），守卫不可行——该事项已由「全局命名统一」指令关闭（见 8.8）** | 教学样例保留语义、只修引用 | 死端设计标注（1301/1308 Span/业务 v2 协同）须团队确认后执行 | `grep -rn "06-协议栈\|00-核心基础设施" docs/10-…/13-*` 零命中；CI 守卫红→绿演练 |
| **B13** 提示词资产可落地通道（衔接 W2 Skills / P2-2 / C5） | 统一占位符规范（名称/类型/必填/默认/脱敏标记）；SYSTEM.md 增版本位；模板元数据 template_id/version/agent/source_doc(120xxx)/checksum；从 120102:203-227/120101:161-172 抽取输出契约作 golden 断言锚点挂 learning_loop；人格统一带间隔号全称（复用 hub `AGENT_ALIAS_MAP` governance_hub.py:40-49）；1300 渲染器参数化并对缺变量报错；模型声明清洗（统一 Qwen3.6-27B-FP8 栈） | 依赖 B11 编号修复（frontmatter 1108xxxx→12xxxx、重复 ID 消除）作下发 key | 不强求 21 篇纯方法论文档模板化（保留方法论定位、标注「非下发资产」） | 首批 5 模板+1300 八家人模板经变量校验下发成功；golden 断言锚点 ≥10 条 |
| B5/B8 素材落点 | B5：迁移 1307 五组正则（修 :410 病态正则）+ 1214 契约签名 + PII 脱敏四类；B8：1208 §3 指标/SLO 表 + 1308 `calculate_slo_compliance` | 迁移时按产线 block/degrade/allow 三值语义映射 | 弱密钥模式与自造 Span 协议不迁移 | 同原批次退出标准 |

### 8.6 二审核心数据指标

| 指标 | 数值 |
|---|---|
| 二审覆盖 | 44 篇 md（~9,400 行）+ 61 代码文件，全量 |
| 可下发提示词模板 | 5 个（4 篇）+ 1300 八家人模板 8 条（需清洗） |
| 1201-1205 技术声明对齐率 | 1/12（仅 Qwen3-Embedding-8B） |
| 死引用/死服务 | 27 文件旧族名引用 / 6 死网关 / ~30 悬空引用 |
| frontmatter 缺陷 | 25 篇旧编号全量 / 1 重复 ID / 2 篇维度字母互换 |
| 夸大/矛盾宣称 | 4 处（AIOps 已实现、留痕不可篡改、FNV-1a 审计链、Production Ready） |
| 原型协议代差 | 1306 mcp_client 2024-11-05 vs 产线 2026-07-28 |
| 安全瑕疵 | debug=True ×1、redis 弱密码回退 ×1、yyc3-secret 弱密钥模式 ×1；硬编码密钥/MD5/SQL 执行均 0 |

### 8.7 二审预期效果与风险提示

- B11+B12 落地后，「名实不符」类发现清零、三层资产恢复可互查性——后续任何复审/新会话的核对成本从「全量重读」降为「查映射索引」。
- 风险：① 八-B 模板修正与对齐表回写涉及提示词/对外表述变更，须走模板版本化 + golden 身份类回归（同 §7.3 对齐税提示）；② 死端标注是评审判断，1301/1308/业务 v2 协同的「弃用」认定须团队确认后执行，本报告仅列证据；③ 蓝图 KPI 数值（↓94%/↑300% 等）均为未注出处的设定值，「GLM-6/Qwen-4.0 不存在」为探查判断——两者均按契约 C1/C6 标注待验证，不作事实断言。
- 数据局限：二审引用的探查定位（file:line）与一审同源同法；批量统计类数字（27/30/110+ 处）来自探查全量 grep，抽验一致（审计链哈希、目录名两项已独立复核）。

### 8.8 执行与决策增补（2026-11-26 第二批）

- **整改第一批已交付**：B1/B2/B11/B12/B13a 随 PR #63（分支 `audit-remediation-batch1`，5 commits）落地——生产文档收口（端口/沙箱/工具面/徽章）、CI 防漂移守卫、代码族死引用清零（84 处）、蓝图层回写（三表/勾选/人格/API 声明/FNV-1a 勘误）、frontmatter 编号修复 25 篇；本地验证 pytest 323+8 全绿。
- **全局命名统一（用户指令 + 两项裁决，本报告建议的「标识符更名评估」以此关闭）**：
  1. 8 个家人标识符全量更名对齐家族全局注册表英文 id——`meta-oracle / navigator / thinker / prophet / bolero / sentinel / master / creative`（agents/ 目录、compose、systemd 实例、hub AGENT_ALIAS_MAP/预算/协同规则/回退链/ACS、tests/evals/golden/mdl、部署脚本；端口 25600-25607 不变）；
  2. **「知遇·伯乐」随全局注册表回正为正名**——CI 命名守卫方向反转（`千里·伯乐/千里伯乐` 判旧称禁入；本报告与 CHANGELOG 作历史证据豁免），蓝图族显示名同步（33 文件），原型示例目录/引用同步；
  3. hub `AGENT_ALIAS_MAP` 重构为三层结构（canonical 英文 id + 中文全名/短名 + legacy 拼音迁移兼容），新增 legacy 归一契约断言；
  4. 顺带消除既有不一致：千行短名 `qianxing`/`qianhang` 双写（统一 navigator）。
  - 执行纪律记录：文档/代码双轨清扫中发生两次同型替换事故（`bole→bolero` 在已含 bolero 文本上二次命中产生 `boleroro`）——sed 双表达式与 Edit 顺序替换均中招，已全局修复并以 grep 归零验证；教训沉淀：**批量替换前须先排除「目标串含源串」的次序问题**。

### 8.9 五维价值矩阵对齐审核（2026-11-26 第三批 · docs/10- 专项）

**正典依据**：用户提供的五维价值矩阵（Value Matrix）——管理职能①（经·管·运·维·营）→ 资源管理②（人·资·进·销·存）→ 能力建设③（标·规·数·智·协）→ 价值创造④（市·创·薪·高·度）→ 自愈链路⑤（自·知·学·治·愈）。

**对齐结论**（逐模块核验）：

| 维度序（正典） | 模块号 | 模块 | 内部维度声明 | 五字域覆盖 | 判定 |
|---|---|---|---|---|---|
| ① 管理职能 | 1201 | 管理职能智能化 | 第一维 ✓ | 经/管/运/维/营 5/5（经营决策·管理流程·运营效率·维护保障·营销增长） | ✅ 对齐 |
| ② 资源管理 | **1204** | 资源管理智能化 | 第二维 ✓ | 人/资/进/销/存 5/5 | ✅ 内容对齐 |
| ③ 能力建设 | **1202** | 能力建设智能化 | 第三维 ✓ | 标/规/数/智/协 5/5 | ✅ 内容对齐 |
| ④ 价值创造 | **1203** | 价值创造智能化 | 第四维 ✓ | 市/创/薪/高/度 5/5 | ✅ 内容对齐 |
| ⑤ 自愈链路 | 1205 | 自愈链路协同化 | 第五维 ✓ | 自/知/学/治/愈 5/5 | ✅ 对齐 |

核心发现：**五模块内部维度声明与五字域覆盖全部正确**（1200 §3.1-3.5 节序亦与正典一致）；唯一错位是**模块目录号 1202/1203/1204 的编号顺序不按维度序排列**（编号序把能力建设排在资源管理之前）。

**不采用项（模块号重排）与原因**：
1. docs/README 编号治理规范明文「编号一旦发布**不复用、不重排**」——重排违反本仓自己的一级规范；
2. 25 篇 frontmatter `file:` 字段与跨层引用（分区索引/12- README/CI 路径/docs/14- 引用）刚于本日收口，重排将再次大范围扰动；
3. 族系代号与维度序解耦已可声明（编号=稳定标识，维度序=语义导航）——语义层补一张映射表即可两全。

**采用项（演进/拓展）**：
1. 「维度序 ↔ 模块号」语义映射表落分区 README（导航按矩阵序、编号保稳定）；
2. 伪代码语法修复 3 处：120405 百分号字面量 ×3（`99%`→`0.99` 等）、120102 变量名截断（`bottlenes`→`bottlenecks`）、120201 演示段 `self` 越界（→ `assessment.`）；
3. Mimosa prompts_overview finding 复核闭环：`prompts_get` 实有 `PROMPT_FILES` 白名单 + `safe_join` 双重防护，判定为对 route 参数模式的启发式保守标记——**不采用改码**（防护已在、加码无增益），以 traversal 探针测试固化为契约（新增 1 用例）。

**演进锚点（五维 → 后续批次素材映射，供 B4-B9 引用）**：⑤ 自愈链路 ↔ B4（不可达目标/终止判断）与 B8（预算/SLO）；③ 数据化治理 ↔ semantic_layer/MDL 已落地部分；① 经营决策 ↔ semantic_query 指标域；② 库存/销售 ↔ E3-2 双路由素材；④ 市场洞察 ↔ prophet 工具面规划。遗留（不在本批）：占位符规范统一（B13）、模块 KPI 数值标注「设定值」。

---

## 9. 参考来源

- 契约依据：YYC3 大模型训练/评测/Agent研发指导角色契约（2026-11-26 生效，C1–C6 补充条款）——长期记忆沉淀版
- 本仓台账：[docs/11 演进完善拓展规划 §9 执行台账](./11-YYC3-Family-AI-Agent-演进完善拓展规划.md) · [docs/13 插件化封装方案](./13-YYC3-Family-AI-Agent-插件化封装方案.md) · [ARCHITECTURE.md](../ARCHITECTURE.md) · [CHANGELOG.md](../CHANGELOG.md)
- 九层架构：[docs/20 人机协同 · 九层架构设计](./20-YYC3-AI-Family-Agent-编程体系/YYC3-AI-Family-Agent-人机协同/AI-FAmily-Agent-智能协同架构/04-YYC3-AI-FAmily-九层架构设计.md)
- 二次审核素材（docs/10- 全量）：[1200 拟人化协同架构](./10-YYC3-提示词工程-企业蓝图/12-YYC3-提示词工程-企业蓝图/1200-提示词工程-AI-FAmily-Agent-拟人化协同架构.md) · [1207 协议栈标准化设计](./10-YYC3-提示词工程-企业蓝图/12-YYC3-提示词工程-企业蓝图/1207-提示词工程-蓝图实战-协议栈标准化设计/README.md) · [1208 全栈可观测性架构](./10-YYC3-提示词工程-企业蓝图/12-YYC3-提示词工程-企业蓝图/1208-提示词工程-蓝图实战-全栈可观测性架构/README.md) · [1209 安全合规与伦理治理](./10-YYC3-提示词工程-企业蓝图/12-YYC3-提示词工程-企业蓝图/1209-提示词工程-蓝图实战-安全合规与伦理治理/README.md) · [1214 工程实现参考手册](./10-YYC3-提示词工程-企业蓝图/12-YYC3-提示词工程-企业蓝图/1214-提示词工程-蓝图实战-工程实现参考手册/README.md) · 1201-1205 实战 30 篇与 13- 代码族 61 文件（探查全量，file:line 见 §8 引用）
- 生态对标（引用 docs/11 §1/§8 调研，2026-10 口径）：Anthropic《Building Effective Agents》· LangGraph · OpenAI Agents SDK · WrenAI / SuperSonic / DB-GPT · Mem0 / Zep / Letta · OTel semantic-conventions-genai
- MCP 规范外部核实（2026-11-26 实查）：[spec 索引与 changelog](https://modelcontextprotocol.io/specification/draft/changelog) · [2026-07-28 发布公告](https://blog.modelcontextprotocol.io/posts/2026-07-28)（最新正式版仍为 2026-07-28；下一版路线 2027-03-30）
- 评测报告入库：evals/reports/{judge_consistency_first, memory_eval_final, semantic_accuracy_first, e13_failover_drill_real, e35_migration_drill_real}.json

---

> 备注：docs/13 Step 5 原预留 `docs/14-` 为 API Reference（sphinx-autodoc）——本报告按 docs/README 编号规则（顺延、不复用）占用 14 号，**API Reference 顺延为 15-**，docs/13 Step 5 表格随其落地时同步修订。

> ***YanYuCloudCube***
> *言启象限 | 语枢未来*
> *Words Initiate Quadrants, Language Serves as Core for Future*
> *万象归元于云枢 | 深栈智启新纪元*
