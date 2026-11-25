---
file: README.md
description: YYC³全栈可观测性架构 — Logs/Metrics/Traces + 分布式追踪 + 告警体系 + 可视化大屏
author: YanYuCloudCube Team <admin@0379.email>
version: v1.0.0
created: 2026-06-03
updated: 2026-06-03
status: published
tags: [可观测性],[分布式追踪],[日志],[指标],[链路],[告警],[可视化]
category: architecture
language: zh-CN
audience: ai-architects,platform-engineers,devops
complexity: advanced
---

> ***YanYuCloudCube***
> *言启象限 | 语枢未来*
> ***Words Initiate Quadrants, Language Serves as Core for Future***
> *万象归元于云枢 | 深栈智启新纪元*

---

# 1208 — 全栈可观测性架构

## 定位

**横向贯穿模块**，为 YYC³ AI Family 体系建立统一的可观测性基础设施，覆盖 Logs(日志)/Metrics(指标)/Traces(链路) 三大支柱。

## 核心理念

**五高架构**: 高可用 | 高性能 | 高安全 | 高扩展 | 高智能
**五标体系**: 标准化 | 规范化 | 自动化 | 可视化 | 智能化
**五化转型**: 流程化 | 数字化 | 生态化 | 工具化 | 服务化
**五维评估**: 时间维 | 空间维 | 属性维 | 事件维 | 关联维

---

## 一、可观测性三支柱架构

### 1.1 全景架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                  YYC³ 全栈可观测性架构                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │                    可视化层 (Visualization)              │  │
│   │  ┌──────────┐  ┌──────────┐  ┌──────────┐               │  │
│   │  │Grafana   │  │Jaeger UI │  │自研大屏  │               │  │
│   │  │指标仪表盘│  │链路追踪  │  │态势感知  │               │  │
│   │  └──────────┘  └──────────┘  └──────────┘               │  │
│   └─────────────────────────────────────────────────────────┘  │
│                              │                                  │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │                    告警层 (Alerting)                     │  │
│   │  ┌──────────┐  ┌──────────┐  ┌──────────┐               │  │
│   │  │SLO 告警  │  │异常检测  │  │告警收敛  │               │  │
│   │  │Prometheus│  │ML-based  │  │降噪去重  │               │  │
│   │  └──────────┘  └──────────┘  └──────────┘               │  │
│   └─────────────────────────────────────────────────────────┘  │
│                              │                                  │
│   ┌───────────────┬───────────────────┬─────────────────────┐  │
│   │   Logs (日志)  │  Metrics (指标)   │  Traces (链路)      │  │
│   │               │                   │                     │  │
│   │ ┌───────────┐ │ ┌───────────────┐ │ ┌─────────────────┐ │  │
│   │ │结构化日志 │ │ │应用指标       │ │ │分布式追踪       │ │  │
│   │ │correlationId│ │ │QPS/延迟/错误率│ │ │OpenTelemetry   │ │  │
│   │ │安全审计   │ │ │Token消耗      │ │ │Span/Trace       │ │  │
│   │ │Agent决策  │ │ │Agent性能     │ │ │Agent调用链      │ │  │
│   │ └───────────┘ │ └───────────────┘ │ └─────────────────┘ │  │
│   │               │                   │                     │  │
│   │ Loki/ELK      │ Prometheus        │ Jaeger/Tempo       │  │
│   └───────────────┴───────────────────┴─────────────────────┘  │
│                              │                                  │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │                    采集层 (Collection)                   │  │
│   │  OpenTelemetry Collector / Fluentd / Vector              │  │
│   └─────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 三支柱分工

| 支柱 | 核心问题 | 数据类型 | 存储方案 | 典型用途 |
|------|---------|---------|---------|---------|
| **Logs** | 发生了什么？ | 结构化日志、审计事件 | Loki / ELK | 问题排查、安全审计、合规追溯 |
| **Metrics** | 系统表现如何？ | 数值指标、时序数据 | Prometheus + VictoriaMetrics | 性能监控、容量规划、SLO追踪 |
| **Traces** | 请求经过了哪些环节？ | Span/Trace 链路 | Jaeger / Tempo | 性能瓶颈定位、依赖分析、调用链追踪 |

---

## 二、结构化日志体系

### 2.1 日志分级标准

| 级别 | 名称 | 含义 | 示例 | 留存策略 |
|------|------|------|------|---------|
| **FATAL** | 致命 | 系统不可用，需立即人工介入 | 数据库连接全部断开 | 永久 |
| **ERROR** | 错误 | 功能异常，需关注处理 | Agent调用失败、SLO偏离 | 90天 |
| **WARN** | 警告 | 潜在风险，需关注 | Token消耗异常、延迟升高 | 30天 |
| **INFO** | 信息 | 正常业务流程记录 | Agent任务开始/完成、决策记录 | 14天 |
| **DEBUG** | 调试 | 开发调试信息 | 工具调用参数、中间结果 | 7天 |
| **TRACE** | 追踪 | 细粒度调用追踪 | 函数调用、参数传递 | 3天 |

### 2.2 YYC³ 统一日志 Schema

```typescript
// 对齐项目已有 security-logger.ts 实现
interface YYC3LogEntry {
  // 基础字段
  id: string;                    // 唯一标识
  correlationId: string;         // 全链路追踪ID（对齐 security-logger.ts）
  timestamp: number;             // Unix 毫秒时间戳

  // 分类字段
  type: "security" | "agent" | "system" | "business" | "performance";
  source: string;                // 来源组件：Agent名称/服务名称
  severity: "FATAL" | "ERROR" | "WARN" | "INFO" | "DEBUG" | "TRACE";

  // 内容字段
  message: string;               // 人类可读消息
  context?: Record<string, unknown>; // 结构化上下文（自动脱敏）

  // 追踪字段
  traceId?: string;              // OpenTelemetry Trace ID
  spanId?: string;               // OpenTelemetry Span ID
  userId?: string;               // 用户标识
  sessionId?: string;            // 会话标识

  // Agent 专属字段
  agentName?: string;            // 发起Agent
  agentAction?: string;          // Agent动作：reason/act/observe/collaborate
  taskId?: string;               // 任务ID
  duration?: number;             // 执行耗时(ms)

  // 性能字段
  tokenUsage?: {
    prompt: number;
    completion: number;
    total: number;
  };
  latency?: number;              // 响应延迟(ms)

  // 安全字段
  securityLevel?: "public" | "internal" | "confidential" | "restricted";
  sanitized?: boolean;           // 是否已脱敏
}
```

### 2.3 Agent 决策日志示例

```json
{
  "id": "log-abc123",
  "correlationId": "corr-xyz789",
  "timestamp": 1717401600000,
  "type": "agent",
  "source": "元启天枢",
  "severity": "INFO",
  "message": "任务分解完成：季度经营分析 → 6个子任务",
  "context": {
    "taskId": "task-20260603-001",
    "subTasks": [
      {"agent": "语枢万物", "action": "data-collection"},
      {"agent": "语枢万物", "action": "kpi-analysis"},
      {"agent": "预见先知", "action": "trend-forecast"},
      {"agent": "创想灵韵", "action": "report-writing"},
      {"agent": "格物宗师", "action": "quality-review"},
      {"agent": "智云守护", "action": "security-audit"}
    ],
    "estimatedDuration": 15000
  },
  "agentName": "元启天枢",
  "agentAction": "plan",
  "taskId": "task-20260603-001",
  "duration": 320,
  "tokenUsage": {
    "prompt": 1500,
    "completion": 800,
    "total": 2300
  }
}
```

---

## 三、指标监控体系

### 3.1 YYC³ Agent 核心指标

| 指标类别 | 指标名称 | 类型 | 单位 | 告警阈值 | 采集频率 |
|---------|---------|------|------|---------|---------|
| **可用性** | `yyc3_agent_uptime` | Gauge | % | <99.9% | 10s |
| **可用性** | `yyc3_agent_error_rate` | Counter | % | >1% | 10s |
| **性能** | `yyc3_agent_latency_p50` | Histogram | ms | >500ms | 10s |
| **性能** | `yyc3_agent_latency_p95` | Histogram | ms | >2s | 10s |
| **性能** | `yyc3_agent_latency_p99` | Histogram | ms | >5s | 10s |
| **吞吐** | `yyc3_agent_requests_total` | Counter | count | — | 10s |
| **吞吐** | `yyc3_agent_qps` | Gauge | req/s | — | 10s |
| **成本** | `yyc3_token_usage_total` | Counter | tokens | — | 60s |
| **成本** | `yyc3_token_cost_estimate` | Gauge | USD | >$100/day | 60s |
| **质量** | `yyc3_agent_decision_accuracy` | Gauge | % | <90% | 60s |
| **质量** | `yyc3_agent_hallucination_rate` | Gauge | % | >5% | 60s |
| **安全** | `yyc3_security_events_total` | Counter | count | >0(P0) | 10s |
| **安全** | `yyc3_content_filter_triggered` | Counter | count | — | 10s |

### 3.2 SLO/SLI/SLA 三级指标

```
┌─────────────────────────────────────────────────────────────────┐
│                    YYC³ Agent SLO 体系                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  SLA (对外承诺)                                                  │
│  ├── 系统可用性 ≥ 99.9%                                         │
│  ├── P95 响应延迟 ≤ 2s                                           │
│  └── 决策准确率 ≥ 90%                                            │
│                                                                 │
│  SLO (内部目标)                                                  │
│  ├── 系统可用性 ≥ 99.95%                                         │
│  ├── P95 响应延迟 ≤ 1.5s                                         │
│  ├── 决策准确率 ≥ 92%                                            │
│  ├── 幻觉率 ≤ 3%                                                 │
│  └── 错误预算消耗 ≤ 50% / 月                                     │
│                                                                 │
│  SLI (实际度量)                                                  │
│  ├── yyc3_agent_uptime                                           │
│  ├── yyc3_agent_latency_p95                                      │
│  ├── yyc3_agent_decision_accuracy                                 │
│  ├── yyc3_agent_hallucination_rate                                │
│  └── yyc3_agent_error_budget_burn_rate                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 3.3 错误预算 (Error Budget)

```
错误预算 = 1 - SLO = 1 - 0.9995 = 0.05%

月度错误预算 = 30天 × 24小时 × 60分钟 × 0.05% = 21.6分钟

告警策略:
├── 错误预算消耗 > 20%: 低优先级告警 (通知)
├── 错误预算消耗 > 50%: 中优先级告警 (升级)
├── 错误预算消耗 > 80%: 高优先级告警 (紧急)
└── 错误预算消耗 > 100%: 冻结发布，全力修复
```

---

## 四、分布式追踪体系

### 4.1 Trace 结构设计

```
┌─────────────────────────────────────────────────────────────────┐
│  Trace: corr-xyz789 (季度经营分析报告生成)                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Span: 言启千行.意图识别         [0ms ──────── 120ms]      │  │
│  │   correlationId: corr-xyz789                              │  │
│  │   tags: {intent: "report_generation", complexity: "high"}  │  │
│  └──────────────────────────────────────────────────────────┘  │
│       │                                                        │
│  ┌────┴────────────────────────────────────────────────────┐   │
│  │ Span: 元启天枢.任务分解          [120ms ─────── 440ms]   │   │
│  │   tags: {subTasks: 6, strategy: "parallel"}              │   │
│  └─────────────────────────────────────────────────────────┘   │
│       │                                                        │
│  ┌────┼────────────┬────────────┬────────────┐                 │
│  ▼    ▼            ▼            ▼            ▼                 │
│  ┌────┐ ┌────────┐ ┌────────┐ ┌────────┐                      │
│  │语枢│ │语枢万物│ │预见先知│ │创想灵韵│                      │
│  │万物│ │KPI分析 │ │趋势预测│ │报告撰写│                      │
│  │数据│ │[440-   │ │[440-   │ │[440-   │                      │
│  │采集│ │ 3240ms]│ │ 2840ms]│ │ 5240ms]│                      │
│  │[440│ └────────┘ └────────┘ └────────┘                      │
│  │ -  │                                                       │
│  │2840│  ┌────────┐ ┌────────┐                                │
│  │ms] │  │格物宗师│ │智云守护│                                │
│  └────┘  │质量审核│ │安全审计│                                │
│          │[5240-  │ │[5240-  │                                │
│          │ 6240ms]│ │ 6040ms]│                                │
│          └────────┘ └────────┘                                │
│                                                                 │
│  Total Duration: 6240ms                                        │
│  Critical Path: 言启千行 → 元启天枢 → 创想灵韵 → 格物宗师       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 调用链属性标注

| 属性名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| `correlation.id` | string | 全链路追踪ID | `corr-xyz789` |
| `agent.name` | string | Agent名称 | `语枢万物` |
| `agent.action` | string | Agent动作 | `data-analysis` |
| `task.id` | string | 任务ID | `task-20260603-001` |
| `mcp.server` | string | 调用的MCP Server | `yyc3-db-server` |
| `mcp.tool` | string | 调用的MCP工具 | `query` |
| `a2a.from` | string | A2A 发起方 | `元启天枢` |
| `a2a.to` | string | A2A 接收方 | `语枢万物` |
| `model.name` | string | 使用的模型 | `GLM-6` |
| `model.tokens` | int | Token消耗 | `2300` |

---

## 五、告警体系

### 5.1 告警分级与响应

| 级别 | 名称 | 触发条件 | 响应时间 | 通知方式 | 升级策略 |
|------|------|---------|---------|---------|---------|
| **P0** | 紧急 | 系统不可用/SLO严重偏离 | 5分钟 | 电话+短信+IM | 5分钟未响应→升级 |
| **P1** | 严重 | 核心功能异常/Agent大面积失败 | 15分钟 | 电话+IM | 15分钟未响应→升级 |
| **P2** | 警告 | 性能下降/错误预算消耗>50% | 30分钟 | IM+邮件 | 1小时未响应→升级 |
| **P3** | 提示 | 单项指标异常/非核心功能 | 2小时 | 邮件 | 4小时未响应→升级 |
| **P4** | 信息 | 趋势预警/建议优化 | 24小时 | 周报 | 无需升级 |

### 5.2 告警规则示例

```yaml
# Agent 延迟告警
- alert: AgentHighLatency
  expr: histogram_quantile(0.95, yyc3_agent_latency_seconds) > 1.5
  for: 5m
  labels:
    severity: P2
  annotations:
    summary: "Agent {{ $labels.agent_name }} P95延迟超过1.5s"
    description: "当前值: {{ $value }}s, 阈值: 1.5s"

# Token消耗异常
- alert: TokenUsageSpike
  expr: rate(yyc3_token_usage_total[5m]) > 1000
  for: 5m
  labels:
    severity: P3
  annotations:
    summary: "Token消耗速率异常升高"
    description: "当前速率: {{ $value }}/s"

# 安全事件告警
- alert: SecurityEvent
  expr: yyc3_security_events_total > 0
  for: 1m
  labels:
    severity: P0
  annotations:
    summary: "检测到安全事件"
    description: "事件数: {{ $value }}, Agent: {{ $labels.agent_name }}"
```

### 5.3 告警收敛与降噪

```
告警收敛策略:
├── 相同Agent+相同指标 → 5分钟内合并为一条
├── 同一Trace下的多个告警 → 聚合为根因告警
├── 已知维护窗口 → 自动静默
├── 自愈成功 → 自动关闭
└── 告警风暴（>50条/分钟）→ 自动降级为汇总通知

告警通知渠道:
├── P0: 企业微信 + 短信 + 电话
├── P1: 企业微信 + 短信
├── P2: 企业微信
├── P3: 邮件
└── P4: 周报汇总
```

---

## 六、可视化大屏设计

### 6.1 态势感知大屏布局

```
┌─────────────────────────────────────────────────────────────────┐
│                  YYC³ Agent 态势感知大屏                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │  Agent 健康状态        │  │  系统可用性   │  │  错误预算     │ │
│  │  ┌──┐┌──┐┌──┐┌──┐   │  │              │  │              │ │
│  │  │天││千││万││先│   │  │   99.97%    │  │   32.5%      │ │
│  │  │枢││行││物││知│   │  │   ↑ 0.02%   │  │   剩余67.5%  │ │
│  │  └──┘└──┘└──┘└──┘   │  │              │  │              │ │
│  │  ┌──┐┌──┐┌──┐┌──┐   │  └──────────────┘  └──────────────┘ │
│  │  │伯││守││宗││灵│   │                                      │
│  │  │乐││护││师││韵│   │  ┌──────────────┐  ┌──────────────┐ │
│  │  └──┘└──┘└──┘└──┘   │  │  Token消耗    │  │  安全态势     │ │
│  └───────────────────────┘  │              │  │              │ │
│                              │  12.5K/min   │  │  🟢 正常     │ │
│  ┌───────────────────────┐  │  ↓ 3.2%      │  │  0事件/24h   │ │
│  │  Agent 调用拓扑图      │  └──────────────┘  └──────────────┘ │
│  │                       │                                      │
│  │   [实时Agent间通信]    │  ┌──────────────────────────────┐   │
│  │   关系图+流量标注      │  │  最近告警 (5条)               │   │
│  │                       │  │  ──────────────────────────── │   │
│  └───────────────────────┘  │  06-03 10:23 P2 语枢万物延迟  │   │
│                              │  06-03 10:15 P3 Token消耗异常 │   │
│  ┌───────────────────────┐  │  06-03 09:58 P4 缓存命中率低  │   │
│  │  P95 延迟趋势 (24h)    │  │  06-03 09:45 P2 预见先知超时 │   │
│  │  ┌───────────────────┐ │  │  06-03 09:30 P3 知识库查询慢 │   │
│  │  │   📈 折线图       │ │  └──────────────────────────────┘   │
│  │  └───────────────────┘ │                                      │
│  └───────────────────────┘  ┌──────────────────────────────┐   │
│                              │  决策准确率趋势 (7天)         │   │
│  ┌───────────────────────┐  │  ┌──────────────────────────┐│   │
│  │  Agent 任务吞吐量      │  │  │   📊 柱状图              ││   │
│  │  ┌───────────────────┐ │  │  └──────────────────────────┘│   │
│  │  │   📊 堆叠柱状图   │ │  └──────────────────────────────┘   │
│  │  └───────────────────┘ │                                      │
│  └───────────────────────┘                                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 6.2 大屏技术选型

| 组件 | 技术选型 | 原因 |
|------|---------|------|
| 指标存储 | Prometheus + VictoriaMetrics | 高性能时序数据库 |
| 日志存储 | Loki + ELK | 轻量级+全文检索 |
| 链路存储 | Jaeger / Tempo | 开源+兼容OpenTelemetry |
| 可视化 | Grafana | 统一仪表盘+告警 |
| 拓扑图 | Cytoscape.js / D3.js | 动态拓扑渲染 |
| 实时推送 | WebSocket + SSE | 低延迟数据推送 |

---

## 七、与项目代码库对齐

| 可观测性组件 | 代码实现 | 状态 |
|-------------|---------|------|
| 结构化日志 | `src/app/lib/security-logger.ts` ✅ | 已就绪 |
| correlationId 追踪 | `security-logger.ts` generateCorrelationId() ✅ | 已就绪 |
| SSE 流式推送 | `src/app/lib/sse-client.ts` ✅ | 已就绪 |
| 双存储（localStorage+IndexedDB） | `src/app/lib/yyc3-storage.ts` ✅ | 已就绪 |
| OpenTelemetry SDK | 待创建 `src/app/lib/telemetry.ts` | 规划中 |
| Prometheus 指标导出 | 待创建 `src/app/lib/metrics.ts` | 规划中 |
| 告警引擎 | 待创建 `src/app/lib/alert-engine.ts` | 规划中 |
| 可视化大屏 | 待创建 `src/app/components/ObservabilityDashboard.tsx` | 规划中 |

---

## 八、实施路线图

### Phase 1：基础可观测（2026 Q3）
- [ ] OpenTelemetry SDK 集成
- [ ] 统一日志 Schema 落地
- [ ] 核心指标采集与导出
- [ ] 基础 Grafana 仪表盘

### Phase 2：深度可观测（2026 Q4）
- [ ] 分布式追踪全链路覆盖
- [ ] SLO/SLI 自动计算与告警
- [ ] Agent 拓扑实时可视化
- [ ] 告警收敛与降噪

### Phase 3：智能可观测（2027 Q1-Q2）
- [ ] ML-based 异常检测
- [ ] 根因自动定位
- [ ] 态势感知大屏
- [ ] 可观测性即服务

---

## 变更历史

| 版本 | 日期 | 变更内容 | 作者 |
|------|------|---------|------|
| v1.0.0 | 2026-06-03 | 初始版本，全栈可观测性架构设计 | YanYuCloudCube Team |

---

<div align="center">

> 「***YanYuCloudCube***」
> 「***<admin@0379.email>***」
> ***Words Initiate Quadrants, Language Serves as Core for the Future***

**© 2025-2026 YYC³ Team. All Rights Reserved.**
</div>