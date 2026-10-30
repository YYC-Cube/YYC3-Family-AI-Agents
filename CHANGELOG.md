# Changelog

本仓库所有显著变更将记录于此文件。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，
版本遵循 [Semantic Versioning](https://semver.org/lang/zh-CN/)。

> 标签体系：`vX.Y.Z`（版本）｜`component/*-vX.Y.Z`（组件）｜`milestone/*`（里程碑），详见 [README「版本与标签」](README.md#️-版本与标签)。

## [Unreleased]

### Added

- **E1-1 SSE 流式对话**：`POST /chat/stream` 以 `text/event-stream` 逐 delta 转发 vLLM 流（`stream_options.include_usage` 获取真实用量）——`meta/delta/done/error` 四类事件、`X-Correlation-ID` 响应头；frozen 检查/审计/预算/协同/telemetry 上报与 `/chat` 完全同构，客户端断连经生成器 `finally` 兜底 `partial` 上报（审计链不因流式而缺口）；生成器不触请求上下文（规避 werkzeug 3.1 `request_ctx` 弹栈错乱）；契约测试 6 例（`tests/integration/test_streaming.py`）
- **E1-5 供应链自动化**：`security.yml`——每周一 pip-audit 审计运行时与测试依赖（高危即红）+ anchore/sbom-action 产出 SPDX JSON SBOM 附件；`dependabot.yml`——pip 与 github-actions 双生态周更
- **E1-4 OTel GenAI 语义对齐**：telemetry 新增 `genai_attrs()` 属性组（`gen_ai.system/operation.name/request.model/agent.name`，对齐 semantic-conventions-genai Development 子集），`trace_span/record_event` 支持 attrs 字典（点号键）；/chat 与流式推理 span 及响应事件挂载 `gen_ai.*` 与 usage 双计数，自有字段并存零破坏；降级日志同步携带属性负载
- **E1-3 缓存与降级矩阵**：语义缓存（`YYC3_CHAT_CACHE_TTL/MAX`，键=模型+全量 messages+采样参数；命中可观测于 `/status`；流式命中单 delta 重放且预算零计费）+ vLLM 主备 failover（`VLLM_ENDPOINT_BACKUP`，4xx 不切换、5xx/连接异常自动切备援，降级即审计 `model_degraded`）
- **E1-2 评估基线**：`evals/golden/golden_cases.json` 首批 24 例（8 家人 × 身份/领域/边界，含注入拒绝与越权负例）+ `evals/run_evals.py` 双轨评估（规则断言零 LLM 离线可跑 + LLM-judge 可选钩子）+ SSRF 边界校验；`tests/evals` 8 例结构门禁随 CI 全量运行
- **E3-3 持久化执行 MVP**：`durable.py` 步骤级 checkpoint（SQLite 自包含 data/durable.db，correlation_id+请求指纹+步骤唯一约束）+ /chat 管线接入——context_injection 与 llm_inference 完成即落 checkpoint，同 cid+指纹重入复用产物（LLM 步骤恢复零 vLLM 调用、预算零计费，响应含 `resumed_steps`）；失败步骤不落 checkpoint（重入自动重执行）；conftest 全局隔离夹具防持久库跨运行残留
- **README 对齐实况完整升级**：顶图 `public/yyc3-family.png`（1800×450 原尺寸）；徽章七组开源级重构（构建质量/运行时部署/协议互通/评估与记忆/治理安全/社区规范/家族 1+8）；特性表十项；协议互通链路图与流式·持久化变体说明；使用指南补 A2A 示例；API 表补 /a2a · agent.json · /mcp · 语义记忆；目录/技术栈/快速开始/版本段全面对齐 E1+E2 收官与 E3 启动
- **E2-3 分层记忆 Semantic 首批**：`memory_semantic.py`（自包含 SQLite 零外部依赖）——Mem0 式三步：规则抽取 MVP（身份/偏好/归属/事实声明四类）→ 去重合并（hits+1 置信度 +0.1 封顶 1.0）→ 读取时按天指数衰减（半衰期 30 天）低于阈值沉睡不删；`governance_hub` 四端点 `/memory/semantic/{store,recall,forget,list}`；**增/改/删全量入审计链**（memory_store/update/forget，先提交再审计防跨连接锁库）
- **E2-1 MCP 客户端**：`mcp_client.py` stateless JSON-RPC 2.0 客户端（initialize/ping/tools.list/tools.call，X-API-Key + X-Correlation-ID 贯穿，`McpTransportError`/`McpProtocolError` 双异常）；SSRF 边界校验；回环联调 10 例（真实 HTTP 全链：握手/401/调用/cid 入审计链）
- **E2-5 A2A 端点**：`/.well-known/agent.json` 发现卡（capabilities.streaming/技能标签）+ `POST /a2a` JSON-RPC（message.send / tasks.get）；任务状态映射（护栏拒绝→rejected、上游失败→failed、成功→completed）；`/chat` 逻辑抽取为 `_execute_chat` 管线函数供 /chat 与 A2A 双端共用（契约零变化）
- **E2-4 护栏管线**：`guardrails.py` 输入注入检测分级处置（七类规则：指令覆盖/提示词窃取/越狱/护栏绕过/破坏性命令/SSRF 探测/密钥探测；高危 block→422、中危 degrade→放行留痕）+ 输出脱敏（私钥块/Token 字面量/键值对/AWS AKIA → `[REDACTED]`）；/chat 与 /chat/stream 双路径接入，guardrail_block/degrade/redact 三事件闭环审计链；注入样本集拦截率 100%、误杀 0
- **E2-2 治理中枢 MCP server**：`POST /mcp` stateless JSON-RPC 2.0（对齐 MCP 2026-07-28 规范子集）——initialize 协商/ping/tools.list/tools.call，治理工具三件（预算仪表盘/审计检索/家人状态）；零信任鉴权沿用；tools/call 全量入审计链；kill-switch 刻意不经 MCP 暴露
- **E1 规划指导**：`docs/11-YYC3-Family-AI-Agent-演进完善拓展规划.md`——大数据 Agent 生态对标（编排/协议/语义层/记忆/观测五维）+ 差距定级 + E1/E2/E3 三阶段路线 + 生产落地检查清单 + 执行进度台账
- **README 升级**：顶图换新 `public/yyc3-aifamily.png`（1800×450 原尺寸，复用 `YYC-Cube/public/YYC3-README-顶图` 家族资产）；徽章体系五组重构（构建质量/运行时部署/治理安全/社区规范/家族 1+8，新增真实 CI 徽章与 SSE/零信任/审计链/OTel/pip-audit 能力徽章）；使用指南补 `/chat/stream` 流式示例；新增核心文档导航
- **可视化交互体系设计（中英双语）**：`docs/12-YYC3-Family-AI-Agent-可视化交互体系设计.md`——六条设计原则、信息架构、组件体系（KPI 卡/家族行/审计表）、交互契约（30s 轮询降级保活/窗口切换/cid→Jaeger 深链）、**SSE 流式 UX 协议**（meta/delta/done/error → UI 状态唯一映射）、视觉令牌表与演进路线 R1-R5，全部取材自 `dashboard.html` 实码与 E1-1 流式契约
- **P0-2 零信任端点认证**：`governance_hub.py` 与 `agent_server.py` 各自引入 `before_request` 认证中间件——写操作（POST/PUT/DELETE/PATCH）须持有效 `X-API-Key`（`hmac.compare_digest` 恒时比较）；读操作与 `/health` 豁免；未配置 Key 时保持本地开放模式
- Agent 侧 4 个治理上报函数（审计/预算/上下文注入/协同检查）自动携带 `X-API-Key`（`_gov_headers()`）
- `docker-compose.yml` 注入 `GOVERNANCE_API_KEY` / `AGENT_API_KEY`（`${VAR:?}` 缺失即启动报错，fail-fast）；`.env.example` 同步模板与说明
- **P0-3 预算窗口惰性重置**：`TokenBudgetManager._ensure_windows()` 基于窗口键（日 `YYYY-MM-DD` / ISO 周 `YYYY-Www` / 月 `YYYY-MM`，UTC 对齐）检测跨窗自动清零计数器——`record_usage` 与 `_check_budget` 双入口挂载，冷启动（空键）不误清；修复原 `last_reset_*` 死字段导致日界永不重置、周/月窗口无任何重置机制的缺陷，零外部定时器依赖
- **P1-2 correlation_id 贯穿**：`/chat` 生成 UUID（支持调用方传入 `correlation_id` 复用）贯穿一次对话全部治理上报（chat_request/context_inject/budget_record/chat_response/collaboration_check/frozen_block），并随响应体返回调用方
- **P1-3 SQLite 并发加固**：`connect_db()` 统一连接工厂——WAL 日志模式（读写不互斥）+ `busy_timeout=10000`（防锁冲突）+ `synchronous=NORMAL`（性能/持久平衡），替换全部 16 处裸连接
- **P2-1 UAT 人设一致性测试**：`tests/uat/test_persona_consistency.py` 82 例静态人设契约——8 位家人 × (三件套存在性/名号跨文件一致/角色/座右铭三源对齐/端口热线注册/五维职能+约束+誓言章节/MBTI/旧称禁入/与 hub 注册表对齐)；LLM 问答抽检属部署后验收范畴
- **P2-2 模板版本化下发**：hub `/prompts/<agent>`（三件套清单含 sha256/size/mtime）+ `/prompts/<agent>/<file>`（text/json 双格式）——复用 `AGENT_ALIAS_MAP` 归一（全名/短名同源），`PROMPTS_SOURCE_DIR` 环境变量适配容器挂载
- **P2-3 telemetry 可观测门面**：新增 `telemetry.py`——OTel 可选依赖（安装即真 span，未安装降级结构化 JSON 日志）+ `correlation_id` 全链路贯穿 + 内存指标快照 + hub `/metrics` 只读端点；agent `/chat` 主链路接入 frozen_check/context_injection/llm_inference 三阶段 span
- **P2-4 LLM 实答 UAT**：`tests/uat/test_llm_persona.py` 8 例身份抽检——环境门控（`YYC3_UAT_LLM=1` + vLLM 可达方执行，默认 skip），断言回答命中名号关键词防人设漂移
- **P3-1 生产全链路验收脚本**：`deploy/acceptance.sh`——7 组验收（基础健康/模板下发/可观测/零信任认证/correlation_id 端到端/LLM 实答 UAT/Jaeger span 导出），生产服务器一条命令验收，退出码=失败数；本机已用裸进程拉起 hub+agent 完成核心端点冒烟
- **P3-2 可观测栈接入**：telemetry 支持 `YYC3_OTLP_ENDPOINT` OTLP/HTTP span 导出（服务名 `yyc3.family-ai`）；compose 新增 `observability` profile——`otel-collector`（4317/4318）+ `jaeger` all-in-one（UI 16686），按需启动不增加常驻资源
- **P3-3 CI 测试门禁**：新增 `unit-tests` job——安装 `requirements-dev.txt` 后 `pytest tests/ -q` 全量门禁（单元/集成/UAT 静态契约，LLM 实答自动门控 skip），失败时上传测试产物；新增 `requirements-dev.txt` 依赖清单
- **P4-1 治理中枢 Web Dashboard**：新增 `dashboard.html`（单文件零依赖，暗色主题 + 紫/青家族设计语言，对齐 YYC3-APP-HUB 生态）——6 项 KPI（在册/事件/24h 高危/Token/协同/熔断）+ 8 位家人状态与日预算进度条（>80% 变红）+ 审计追踪表（含 correlation_id），30s 自动刷新；hub 根路径 `/` 挂载（读路径免认证），JSON API 契约不变
- **P4-2 Dashboard 增强**：预算窗口日/周/月切换（复用 P0-3 三窗口服务端字段）+ correlation_id 点击跳转 Jaeger trace 检索（`window.JAEGER_BASE` 可配置，默认 127.0.0.1:16686）+ 预算显示 used/limit

### Changed

- 测试矩阵 47 → 154 passed + 8 skipped：P0-3 +7（窗口）、P1-2 +3（贯穿）、P1-3 +3（WAL/并发写/工厂统一）、P2-1 +82（人设契约）、P2-2 +6（模板下发）、P2-3 +8（telemetry/接线）、P2-4 +8（门控 skip）
- Agent 5 个治理上报函数异常处理由静默 `pass` 改为 `logger.debug`（含 correlation_id 上下文），治理中枢故障可观测且不阻塞对话

### Fixed

- **P1-1 命名残留清零**：`docker-compose.yml` 3 处「知遇·伯乐/知遇伯乐」（端口规划注释/服务注释/`AGENT_LABEL`）→「千里·伯乐/千里伯乐」；`governance_hub.py` ACS `display_name` 残留同步纠偏；CI 命名门禁扩展覆盖 `*.yml`/`*.yaml` 及无间隔号变体「知遇伯乐」

### Planned

- P1：telemetry 可观测 SDK 嵌入 + 治理中枢 `/prompts/*` 模板服务
- P2：A2A/MCP 协议栈接入与业务规则引擎场景化

## [3.1.0] - 2026-09-14

### Added

- 8 位家人 Agent 统一 Flask 服务 `agent_server.py`（v3.1，能力矩阵 + 降级 + 治理上报）
- 治理中枢 `governance_hub.py` v1.0.0（审计/预算/熔断/协同/图谱/记忆，25 端点）
- 8 位家人身份档案体系（`agents/*/IDENTITY.md`、`SOUL.md`、`SYSTEM.md`）
- 生产部署体系（`deploy/install.sh|ops.sh|verify.sh` + 12 个 systemd 单元 + docker-compose 双模式）
- 文档库 `docs/`（编程体系 + 企业蓝图双维度，5 个专题索引）
- 提示词工程蓝图 `docs/10-YYC3-提示词工程-企业蓝图`（14 模块 33 篇，CO-STAR+CRAFT 规范 / MCP+A2A 协议栈 / 可观测 / 安全合规）
- 示例代码库 `examples/13-YYC3-企业蓝图-代码示例`（9 大模块 60+ 文件）
- 版本标签体系（`v3.1.0` + 组件标签 ×2 + 里程碑标签）

### Changed

- 命名归一：「知遇·伯乐」→「千里·伯乐」（55 文件 190 处，以生产层为权威事实源）
- 12 系列 README 模块总览对齐实际目录（1202=能力建设/1203=价值创造/1204=资源管理）
- 仓库架构重组：12 系列迁入 `docs/10-*`，13 系列迁入 `examples/13-*`

### Fixed

- docs/ 跨目录失效链接（010300/010305 旧编号 → 实际路径）
- 家人档案 README 中指向不存在「品牌标识」文档的链接
- 管理蓝图索引中 `/Volumes/Max/...` 外部卷绝对路径

## [3.0.0] - 2026-08-30

### Added

- 治理中枢雏形（/health /agents /kill /audit）
- docker-compose 容器编排与 GPU 直通（N2 DGX Spark）

[Unreleased]: https://github.com/YYC-Cube/YYC3-Family-AI-Agents/compare/v3.1.0...HEAD
[3.1.0]: https://github.com/YYC-Cube/YYC3-Family-AI-Agents/compare/v3.0.0...v3.1.0
[3.0.0]: https://github.com/YYC-Cube/YYC3-Family-AI-Agents/releases/tag/v3.0.0
