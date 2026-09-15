# Changelog

本仓库所有显著变更将记录于此文件。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，
版本遵循 [Semantic Versioning](https://semver.org/lang/zh-CN/)。

> 标签体系：`vX.Y.Z`（版本）｜`component/*-vX.Y.Z`（组件）｜`milestone/*`（里程碑），详见 [README「版本与标签」](README.md#️-版本与标签)。

## [Unreleased]

### Planned
- P0：生产端点接入零信任网关认证（复用 `examples/13-YYC3-企业蓝图-代码示例/1307-代码示例-安全合规/zero_trust_gateway.py`）
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
