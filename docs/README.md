# YYC³ Family AI Agent — 文档中心

> ***YanYuCloudCube***
> *言启象限 | 语枢未来*
> ***Words Initiate Quadrants, Language Serves as Core for Future***
> *万象归元于云枢 | 深栈智启新纪元*
> ***All things converge in cloud pivot; Deep stacks ignite a new era of intelligence***

---

## 🗺️ 文档地图

```
docs/                                        ← 85 篇 Markdown · 6 个一级分区
├── README.md                                ← 唯一导航入口（本页）+ 文档规范
│
├── 10-YYC3-提示词工程-企业蓝图/              ← 提示词工程蓝图 · 15 模块 · 41 篇
│   ├── README.md                            ← 模块总索引（1200-1214）
│   ├── 1200-…拟人化协同架构.md               ← 1+8 Agent 协同体系设计
│   ├── 1201-1205/                           ← 五维价值矩阵实战（25 篇 + 5 索引）
│   ├── 1206-1209/                           ← 平台横切（规范/协议栈/可观测/安全）
│   ├── 1210-1213-…                          ← 治理层（大纲/路线图/算力/总纲）
│   └── 1214-…工程实现参考手册/               ← 纵向深化（代码骨架 + API 契约）
│
├── 11-YYC3-Family-AI-Agent-演进完善拓展规划.md   ← 大数据 Agent 对标 · E1/E2/E3 路线 + 执行台账
├── 12-YYC3-Family-AI-Agent-可视化交互体系设计.md ← 治理中枢 Dashboard 可视化/交互/SSE-UX（中英双语）
│
├── 20-YYC3-AI-Family-Agent-编程体系/         ← 技术维度 · 18 篇
│   ├── README.md                            ← 编程体系索引
│   ├── YYC3-AI-Family-Agent-人机协同/        ← 五维五高五标五化 · 情感文化总铭 · 九层架构
│   └── YYC3-AI-Family-Agent-家人档案/        ← 8 位家人技术维度档案
│
├── 30-YYC3-Family-AI-Agent-企业蓝图/         ← 管理维度 · 19 篇
│   ├── README.md                            ← 企业蓝图索引
│   ├── YYC3-Family-AI-Agent-家人档案/        ← 8 位家人企业管理维度档案
│   ├── YYC3-Family-AI-Agent-情感公约/        ← 协同公约与情感规范（3 篇）
│   └── YYC3-Family-AI-Agent-管理蓝图/        ← 五维总纲 · 拟人化协同架构
│
└── 90-归档-20260914-会话工作目录/            ← 只读历史归档（审核/修复/总结，4 篇，不再维护）

examples/13-YYC3-企业蓝图-代码示例/            ← 蓝图工程原型（代码示例，不属文档库）
```

---

## 📚 双维度文档体系

| 维度 | 入口 | 定位 |
|------|------|------|
| 🧬 **技术维度** · 编程体系 | [20-YYC3-AI-Family-Agent-编程体系](./20-YYC3-AI-Family-Agent-编程体系/README.md) | 人机协同方法论、九层架构设计、家人技术档案 |
| 🏢 **管理维度** · 企业蓝图 | [30-YYC3-Family-AI-Agent-企业蓝图](./30-YYC3-Family-AI-Agent-企业蓝图/README.md) | 企业管理智能化落地蓝图、情感公约、家人管理档案 |
| 📐 **方法维度** · 提示词工程 | [10-YYC3-提示词工程-企业蓝图](./10-YYC3-提示词工程-企业蓝图/README.md) | 五维价值矩阵、平台横切规范、工程实现参考 |

### 推荐阅读路径

```
新成员入门：docs/README（本页） → 30-企业蓝图/README → 20-人机协同/01-五维五高五标五化 → 20-家人档案
架构深潜：  20-人机协同/智能协同架构（九层系列 5 篇） → 30-管理蓝图/拟人化协同架构 → 10-1200
工程落地：  10-1206 编写规范 → 10-1214 工程实现参考手册 → docs/11 演进规划 §9 执行台账
文化建设：  30-情感公约（3 篇） → 情感文化总铭 → 家族誓言（各家人档案）
历史追溯：  90-归档（只读，仅用于审阅与决策留痕）
```

---

## 📏 文档规范（新增/修改文档必须遵循）

### 1. 目录与编号

| 分区 | 编号规则 | 用途 |
|------|---------|------|
| `10-` | 4 位模块号（1200-1214），模块内 6 位文档号（120101） | 提示词工程蓝图 |
| `20-` / `30-` | 二维体系，内部按主题目录聚合，不再细分编号 | 技术维度 / 管理维度 |
| `90-` | `90-归档-YYYYMMDD-<主题>/` | 会话归档，只读 |
| 根级文件 | `NN-<主题>.md`（如 `11-…` / `12-…`） | 跨分区单篇长文 |

- 编号一旦发布**不复用、不重排**；新增模块顺延最大号（当前最大 1214），禁止与既有号段冲突。
- 新增一级分区按 10 → 20 → 30 → 90 顺序插入，归档恒为最后。

### 2. 文件与目录命名

- 格式：`<编号>-<主题>.md` / `<编号>-<主题>/`；词间统一半角连字符 `-`，不使用空格、下划线、全角符号。
- 目录/文件名统一使用仓库正式名 **`YYC3-Family-AI-Agent`**（如 `30-YYC3-Family-AI-Agent-企业蓝图`）；正文中的品牌写法 `FAmily` 属于视觉表达，可保留。
- 每个可展开目录必须有 `README.md` 作为索引，索引内链接使用仓库相对路径。

### 3. 文档元数据（front matter）

推荐使用统一 12 字段（当前 55/85 篇已覆盖，新文档必须补齐）：

```yaml
---
file: <文件名>
description: <一句话说明>
author: YanYuCloudCube Team <admin@0379.email>
version: v1.0.0
created: YYYY-MM-DD
updated: YYYY-MM-DD
status: draft | review | published | archived
tags: [..]
category: <practice | architecture | governance | ...>
language: zh-CN
audience: <managers | ai-engineers | ...>
complexity: <basic | intermediate | advanced>
---
```

### 4. 链接规范

- 仅使用**仓库相对路径**（如 `./xxx.md`、`../xxx/README.md`）；禁止 `file:///Users/...` 等本机绝对路径。
- 跨分区引用必须带分区编号（如 `../20-YYC3-AI-Family-Agent-编程体系/README.md`）。
- 目录级引用指向其 `README.md`，不指向目录本身。
- CI `docs-links` 任务校验：核心文档存在性、旧编号死链（010300/010305）、历史旧称归一。

### 5. 归档与维护

- `90-归档-*` 为只读历史来源：保留原始结论与时间线，不再更新内容、不参与命名归一强制。
- 结论性变更写入 [CHANGELOG.md](../CHANGELOG.md)；规划与验收状态写入 [11- 演进规划](./11-YYC3-Family-AI-Agent-演进完善拓展规划.md)。
- 新增/移动文档时，必须同步更新：本页文档地图、所属分区 `README.md` 索引、以及所有入链文档。

---

## 🔗 仓库关联

| 文档 | 路径 |
|------|------|
| 运行仓 README（架构 · 部署 · API） | [README.md](../README.md) |
| 架构总览（分层/数据流/ADR） | [ARCHITECTURE.md](../ARCHITECTURE.md) |
| 变更日志（Keep a Changelog + SemVer） | [CHANGELOG.md](../CHANGELOG.md) |
| 贡献指南（工作流 + 质量门禁） | [CONTRIBUTING.md](../CONTRIBUTING.md) |

---

<div align="center">

> 「***YanYuCloudCube***」言启象限 | 语枢未来
> 「***Words Initiate Quadrants, Language Serves as Core for the Future***」
> 「***All things converge in cloud pivot; Deep stacks ignite a new era of intelligence***」

**© 2025-2026 YYC³ Team. All Rights Reserved.**

</div>
