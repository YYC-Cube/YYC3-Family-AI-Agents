# Changelog

本仓库所有显著变更将记录于此文件。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，
版本遵循 [Semantic Versioning](https://semver.org/lang/zh-CN/)。

> 标签体系：`vX.Y.Z`（版本）｜`component/*-vX.Y.Z`（组件）｜`milestone/*`（里程碑），详见 [README「版本与标签」](README.md#️-版本与标签)。

## [Unreleased]

### Added

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
