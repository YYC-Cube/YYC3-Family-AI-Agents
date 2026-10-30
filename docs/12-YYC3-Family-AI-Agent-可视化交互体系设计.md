---
file: "12-YYC3-Family-AI-Agent-可视化交互体系设计.md"
title: "YYC³ FAmily-AI Agent · 可视化交互体系设计（中英双语 / Bilingual Design Spec）"
description: "治理中枢 Dashboard 与流式对话工作台的可视化组件体系、交互体系、SSE 事件协议映射、视觉语言与演进路线——基于 dashboard.html 实码与 E1-1 流式契约提炼，中英双语"
author: "YanYuCloudCube Team <admin@0379.email>"
version: "v1.0.0"
created: "2026-10-30"
updated: "2026-10-30"
status: "active"
license: "MIT"
---

# YYC³ 可视化交互体系设计 · Visualization & Interaction Design System

> ***YanYuCloudCube*** · *言启象限 | 语枢未来 · 万象归元于云枢 | 深栈智启新纪元*

> **定位 | Purpose**：本文是治理中枢 Dashboard（`dashboard.html`）与后续流式对话工作台的**可视化与交互体系单一事实源**。所有 UI 变更以本文为契约：组件命名、语义色、事件协议、交互态均由此定义，实现偏离即缺陷。
> This document is the **single source of truth** for the Governance Dashboard and the upcoming streaming chat workbench. All UI changes treat it as the contract: component naming, semantic colors, event protocols, and interaction states are defined here — implementation drift is a defect.

---

## 1. 设计原则 | Design Principles

| # | 中文 | English |
|---|---|---|
| P1 | **奢侈极简**：留白充分、字重对比、每屏一个视觉焦点；装饰为零 | **Luxury minimalism**: generous whitespace, weight contrast, one focal point per view; zero ornament |
| P2 | **数据密度优先**：治理场景要一眼见全貌——KPI 六卡先行，细节按需下钻 | **Density first**: governance demands full situational awareness — six KPI cards up front, detail on drill-down |
| P3 | **语义色恒定**：绿=健康/放行、红=冻结/高危、黄=预算预警、紫=AI/智能、青=可观测/链接——全站唯一映射，禁止复用 | **Constant semantic colors**: green=healthy/allowed, red=frozen/high-risk, yellow=budget-warning, purple=AI/intelligence, cyan=observability/link — one mapping site-wide, never reused |
| P4 | **零依赖**：vanilla JS + CSS 变量，不引框架/图表库——治理面板自身不允许成为供应链面 | **Zero dependency**: vanilla JS + CSS variables, no frameworks or chart libs — the governance panel must not become a supply-chain surface |
| P5 | **防注入内建**：一切外部字符串经 `esc()` 转义后渲染；提示词不是安全边界，DOM 亦然 | **Injection-safe by construction**: every external string renders through `esc()`; prompts are not a security boundary, neither is the DOM |
| P6 | **可追溯**：任何一条治理数据都能经 `correlation_id` 跳转到 Jaeger 还原全链 | **Traceable**: any governance datum links back to the full chain in Jaeger via `correlation_id` |

---

## 2. 信息架构 | Information Architecture

```
┌ Header ────────────────────────────────────────────────┐
│ Logo(渐变Y) · 标题+副标 · 连接状态 pill · 手动刷新按钮 │
├ KPI 条（六卡，auto-fit ≥150px 自适应栅格）──────────────┤
│ Agent 在册 │ 治理事件累计 │ 24h高危 │ 24hToken │ 24h协同 │ 预算熔断 │
├ 双卡栅格（≤900px 折叠单列）────────────────────────────┤
│ ┌ Agent 家族状态×Token预算 ┐ ┌ 治理事件审计（15条）┐ │
│ │ [日|周|月] 窗口切换       │ │ 时间·Agent·动作·风险·cid │ │
│ └──────────────────────┘ └─────────────────────┘ │
├ Footer ────────────────────────────────────────────────┤
│ /health · /metrics · /dashboard(JSON) │ 英文署名行     │
└────────────────────────────────────────────────────┘
```

**English**: Header (brand mark + connection pill + manual refresh) → six-card KPI strip → two-card grid (family status × token budget with day/week/month window switch ‖ audit trail, latest 15) → footer endpoint links. The grid collapses to a single column at ≤900px.

数据源 | Data sources：`GET /dashboard`（聚合计数 + 家族状态 + 预算窗口）与 `GET /audit/trail?limit=15`，**30 秒轮询**（`setInterval(loadAll, 30000)`）+ 手动刷新按钮双通道。

---

## 3. 可视化组件体系 | Component System

### 3.1 KPI 卡 | KPI Card

- 结构：`num`（26px 等宽粗体）+ `lbl`（11px 弱化说明）；语义态类 `good / warn / bad` 直接改写数值色。
- 六卡语义：在册 Agent（good）· 治理事件累计（中性）· 24h 高危事件（>0 → bad）· 24h Token 消耗（`toLocaleString` 千分位）· 24h 协同触发（中性）· 预算熔断 Agent 数（>0 → warn）。
- **English**: number-first card with muted label; semantic state class recolors the numeral. High-risk > 0 flips to red; any budget-frozen agent flips the last card to yellow.

### 3.2 Agent 家族行 | Family Row

- 五段式布局：家人图标（emoji）→ 双语名（中文名 + 等宽短名）→ 状态 tag（`active` 绿 / `frozen` 红）→ 预算条 → 百分比与用量。
- 预算条：6px 圆角轨道，紫→青渐变填充；**≥80% 切换为黄→红渐变（hot 态）**——预算预警不用文字告警，用色彩本身。
- 窗口切换：日/周/月 pill 组（激活态 = 品牌渐变底白字），切换即全量重渲染（客户端持有 `curWindow` 状态）。
- **English**: five-segment row (icon → bilingual name → state tag → budget bar → usage). The bar renders a purple-cyan gradient that **switches to yellow-red above 80%** — budget warnings are color-borne, not text-borne. Window pills re-render the panel client-side.

### 3.3 审计追踪表 | Audit Trail Table

- 列：时间（截 `MM-DD HH:MM:SS`）· Agent（短名→中文名映射，映射表 `FAMILY` 常量唯一维护）· 动作 · 风险 tag（low 绿 / medium 黄 / high·critical 红）· `correlation_id`（截 8 位）。
- **cid 可点**：虚线下划线样式暗示可交互，点击在 Jaeger 新窗检索 `service=yyc3.family-ai` + `correlation_id` 标签——P6 可追溯原则的落地件。
- **English**: audit rows render via the single `FAMILY` mapping constant; the truncated `correlation_id` is a dashed-underline link that opens a Jaeger search deep-link — the tangible form of the traceability principle.

---

## 4. 交互体系 | Interaction System

| 交互 | 行为契约 | Contract |
|---|---|---|
| 轮询刷新 | 30s `Promise.all` 并行拉取双端点；任一失败 → 连接 pill 变「连接失败」，**不清空已渲染数据**（降级保 last-known-good） | 30s polling; on failure the pill reports disconnected and **stale data is kept** (last-known-good degradation) |
| 手动刷新 | Header 按钮即时 `loadAll()` | Manual refresh button triggers immediate reload |
| 窗口切换 | 纯客户端状态切换，不重拉数据（预算三窗口同响应体返回） | Window switch is client-side state only — all three windows arrive in one payload |
| cid 下钻 | `openTrace()` 组装 Jaeger 深链，`noopener` 新窗 | cid click opens a Jaeger deep-link in a new, `noopener` window |
| Jaeger 地址 | `window.JAEGER_BASE` 可被宿主注入覆盖（默认 `127.0.0.1:16686`） | Jaeger base is host-injectable via `window.JAEGER_BASE` |
| 空态/加载态 | 「加载中…」「暂无治理事件」空态文案组件化（`.empty`） | Empty and loading states are componentized |

---

## 5. 流式对话 UX 协议（E1-1 联动）| Streaming Chat UX Protocol

`POST /chat/stream` 的 SSE 事件到界面状态的**唯一映射**（工作台实现必须遵循，不得另造语义）：

| SSE 事件 | 载荷字段 | UI 状态迁移 | English |
|---|---|---|---|
| `meta` | agent / label / role / correlation_id / model | 打开会话卡：家人身份头 + cid 徽标 + 模型名；**cid 徽标即 Jaeger 深链** | Open session card with persona header; the cid badge doubles as the Jaeger link |
| `delta` | content / correlation_id | 追加渲染到消息流（等宽可选；**必须 esc() 后插入**）；逐 token 到达即渲染，不批处理 | Append token to the stream (escaped); render on arrival, no batching |
| `done` | usage / latency_ms / collaboration / timestamp | 完成态：用量与延迟入会话脚注；协同建议以非阻断提示呈现 | Completion footer with usage and latency; collaboration hint renders non-blocking |
| `error` | error / correlation_id | 错误横幅 + 「重试」按钮（以相同 `correlation_id` 重放，治理侧可关联两次尝试） | Error banner with retry replaying the same correlation_id |

工程约束 | Constraints：响应头 `X-Correlation-ID` 与 `meta` 事件二者必含其一即可建立会话；客户端**禁止**在 `done` 前渲染任何汇总性结论；断线重连用「新会话 + 原 cid 引用」实现，不做流内续传（vLLM 流不可恢复）。
The response header `X-Correlation-ID` or the `meta` event establishes the session; no summary may render before `done`; reconnection starts a new stream that *references* the original cid — in-stream resume is impossible by design.

---

## 6. 视觉语言 | Visual Language

| 令牌 | 值 | 语义 | Token / Meaning |
|---|---|---|---|
| `--bg` / `--bg2` | `#0a0a0f` / `#12121a` | 深空底色双层 | Deep-space background, two layers |
| `--v` | `#8b5cf6` | AI / 智能 / 品牌渐变起点 | AI & brand gradient start |
| `--c` | `#06b6d4` | 可观测 / 链接 / 渐变终点 | Observability, links, gradient end |
| `--e` | `#22c55e` | 健康 / active / 通过 | Healthy, active, passing |
| `--r` | `#ef4444` | 冻结 / 高危 / 拒绝 | Frozen, high-risk, denied |
| `--y` | `#eab308` | 预算 / 预警 | Budget, warning |
| `--radius` | `14px` | 卡片圆角 | Card radius |
| `--mono` | SF Mono / Fira Code | 数值与 cid 专用等宽 | Mono for numerals & ids |

字体栈 | Type stack：`-apple-system → PingFang SC → Microsoft YaHei`；标题 18px / 卡题 13px / 正文 12px / 辅助 11px / 标签 10px——**五级字阶，跨级禁用**。
Five type sizes only (18/13/12/11/10px); skipping tiers is prohibited.

---

## 7. 工程约束 | Engineering Constraints

- 单文件自包含（`dashboard.html`，零外部资源）；favicon 为内联 SVG data-URI | Single self-contained file; favicon is an inline SVG data-URI
- 一切动态插值经 `esc()`（`& < > "` 四字符）| All dynamic interpolation passes `esc()`
- 渲染函数纯函数化（`renderKpis/renderAgents/renderEvents` 各自幂等重绘）| Render functions are idempotent pure re-draws
- 面板自身零新增依赖：图表需求先用 CSS bar/渐变满足，图表库引入须过 E1-5 供应链评审 | No new dependencies for the panel itself; any chart lib must pass the supply-chain review (E1-5)

---

## 8. 演进路线 | Roadmap

| 阶段 | 事项 | 对应规划 |
|---|---|---|
| R1 | 流式对话工作台（§5 协议落地，SSE 客户端 + 会话流 UI） | E1-1 |
| R2 | `gen_ai.*` trace 面板联动（span 瀑布替代外跳 Jaeger 的兜底视图） | E1-4 |
| R3 | 语义层 / ChatBI 查询视图（SQL 审计卡片 + dry-plan 校验态可视化） | E3-1/2 |
| R4 | 中英 UI 一键切换（i18n 字典化，本文双语词汇表为初始键表） | — |
| R5 | 无障碍 WCAG AA（对比度审计 + 键盘导航 + aria-live 事件播报） | — |

---

## 9. 术语表 | Glossary

| 中文 | English | 定义 |
|---|---|---|
| 治理事件 | Governance event | 一次审计上报（chat_request / frozen_block / chat_response 等） |
| 预算窗口 | Budget window | 日/周/月三窗计数器，惰性跨窗重置 |
| 熔断 | Kill switch / frozen | Agent 被冻结后拒绝推理（403） |
| 会话 | Session | 一个 correlation_id 覆盖的完整对话生命周期 |
| 事件协议 | Event protocol | SSE `meta/delta/done/error` 四类事件（§5） |

---

> ***YanYuCloudCube***
> *言启象限 | 语枢未来*
> *Words Initiate Quadrants, Language Serves as Core for Future*
> *万象归元于云枢 | 深栈智启新纪元*
