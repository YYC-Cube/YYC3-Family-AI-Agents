---
file: README.md
description: YYC³工程实现参考手册 — 代码骨架 + API契约 + 测试用例 + 部署方案
author: YanYuCloudCube Team <admin@0379.email>
version: v1.0.0
created: 2026-06-03
updated: 2026-06-03
status: draft
tags: [工程实现],[代码骨架],[API契约],[测试用例],[部署方案],[架构参考]
category: engineering
language: zh-CN
audience: developers,backend-engineers,frontend-engineers
complexity: advanced
---

> ***YanYuCloudCube***
> *言启象限 | 语枢未来*
> ***Words Initiate Quadrants, Language Serves as Core for Future***
> *万象归元于云枢 | 深栈智启新纪元*

---

# 1211 — 工程实现参考手册

## 定位

**纵向深化模块**，为 YYC³ AI Family 蓝图的各模块提供可执行的工程实现参考，包括代码骨架、API 契约、测试用例和部署方案。

## 核心理念

**五高架构**: 高可用 | 高性能 | 高安全 | 高扩展 | 高智能

---

## 一、工程目录结构

```
src/app/
├── lib/
│   ├── ai-service.ts           # ✅ AI服务统一调用（含流式）
│   ├── sse-client.ts           # ✅ SSE流式客户端
│   ├── security-logger.ts      # ✅ 结构化安全日志
│   ├── yyc3-storage.ts         # ✅ 双存储策略
│   ├── mcp-client.ts           # 🔲 MCP协议客户端
│   ├── a2a-client.ts           # 🔲 A2A Agent通信客户端
│   ├── agent-card.ts           # 🔲 Agent Card定义
│   ├── telemetry.ts            # 🔲 OpenTelemetry SDK
│   ├── metrics.ts              # 🔲 Prometheus指标导出
│   ├── alert-engine.ts         # 🔲 告警引擎
│   ├── content-filter.ts       # 🔲 内容安全过滤
│   ├── injection-detector.ts   # 🔲 提示词注入检测
│   ├── zero-trust-auth.ts      # 🔲 零信任认证
│   ├── compliance-auditor.ts   # 🔲 合规审计
│   └── security-incident.ts    # 🔲 安全事件响应
│
├── agents/                     # 🔲 Agent实现
│   ├── base-agent.ts           # 🔲 Agent基类
│   ├── tianshu/                # 🔲 元启天枢
│   ├── navigator/              # 🔲 言启千行
│   ├── thinker/                # 🔲 语枢万物
│   ├── prophet/                # 🔲 预见先知
│   ├── recommender/            # 🔲 千里伯乐
│   ├── sentinel/               # 🔲 智云守护
│   ├── master/                 # 🔲 格物宗师
│   └── muse/                   # 🔲 创想灵韵
│
├── components/
│   ├── ObservabilityDashboard.tsx  # 🔲 可观测性大屏
│   ├── AgentTopology.tsx           # 🔲 Agent拓扑图
│   └── PromptStudio.tsx            # 🔲 提示词工作室
│
├── store/                      # ✅ 状态管理
│   ├── family-settings.ts
│   ├── family-sessions.ts
│   └── ...
│
├── hooks/                      # ✅ 自定义Hooks
│   ├── useHostFileSystem.ts
│   └── ...
│
└── __tests__/                  # ✅ 测试
    ├── rf-phase2.test.ts
    └── ...

图例: ✅ 已实现 | 🔲 规划中
```

---

## 二、Agent 基类设计

### 2.1 BaseAgent 契约

```typescript
// src/app/agents/base-agent.ts
import { SecurityLogger } from "../lib/security-logger";
import { SSEClient } from "../lib/sse-client";

export interface AgentIdentity {
  name: string;
  role: string;
  description: string;
  version: string;
}

export interface AgentCapability {
  id: string;
  name: string;
  description: string;
  tags: string[];
  examples: string[];
}

export interface AgentCard {
  identity: AgentIdentity;
  capabilities: AgentCapability[];
  defaultInputModes: ("text" | "structured" | "multimodal")[];
  defaultOutputModes: ("text" | "structured" | "streaming")[];
  authentication: {
    schemes: ("bearer_token" | "api_key")[];
    required: boolean;
  };
  security: {
    tlsRequired: boolean;
    rbacRoles: string[];
  };
  slo: {
    latency: { p50: string; p95: string; p99: string };
    availability: string;
    errorRate: string;
  };
}

export interface AgentTask {
  id: string;
  type: string;
  priority: "low" | "medium" | "high" | "critical";
  deadline?: string;
  input: Record<string, unknown>;
  context: {
    correlationId: string;
    previousTaskId?: string;
    userPreference?: Record<string, unknown>;
  };
}

export interface AgentTaskResult {
  taskId: string;
  status: "completed" | "failed" | "partial" | "cancelled";
  output?: Record<string, unknown>;
  error?: {
    code: string;
    message: string;
    retryable: boolean;
  };
  metrics: {
    duration: number;
    tokenUsage: { prompt: number; completion: number; total: number };
    startTime: number;
    endTime: number;
  };
  artifacts?: Array<{
    name: string;
    type: string;
    url: string;
  }>;
}

export abstract class BaseAgent {
  protected identity: AgentIdentity;
  protected securityLogger: SecurityLogger;
  protected sseClient: SSEClient;

  constructor(identity: AgentIdentity) {
    this.identity = identity;
    this.securityLogger = new SecurityLogger();
    this.sseClient = new SSEClient();
  }

  /** 获取 Agent Card (A2A协议) */
  abstract getAgentCard(): AgentCard;

  /** 执行任务 */
  abstract executeTask(task: AgentTask): Promise<AgentTaskResult>;

  /** 流式执行任务 */
  abstract executeTaskStream(
    task: AgentTask,
    onChunk: (chunk: string) => void
  ): Promise<AgentTaskResult>;

  /** 健康检查 */
  abstract healthCheck(): Promise<{ status: "healthy" | "degraded" | "unhealthy" }>;

  /** 安全审计日志 */
  protected audit(action: string, result: string, context?: Record<string, unknown>): void {
    this.securityLogger.log({
      type: "agent",
      source: this.identity.name,
      severity: "INFO",
      message: `${this.identity.name}: ${action} - ${result}`,
      context,
    });
  }
}
```

### 2.2 Agent 实现示例 (语枢万物)

```typescript
// src/app/agents/thinker/index.ts
import { BaseAgent, AgentCard, AgentTask, AgentTaskResult } from "../base-agent";
import { callAIStream } from "../../lib/ai-service";

export class ThinkerAgent extends BaseAgent {
  constructor() {
    super({
      name: "语枢万物",
      role: "thinker",
      description: "YYC³ AI Family 思考者 — 数据分析与统计建模专家",
      version: "2.0.0",
    });
  }

  getAgentCard(): AgentCard {
    return {
      identity: this.identity,
      capabilities: [
        {
          id: "data-analysis",
          name: "数据分析与统计建模",
          description: "对结构化/非结构化数据进行统计分析、趋势预测",
          tags: ["statistics", "analytics", "forecasting"],
          examples: ["分析本月销售数据趋势", "计算各部门KPI完成率"],
        },
        {
          id: "root-cause-analysis",
          name: "故障根因分析",
          description: "基于日志/指标/链路数据定位故障根因",
          tags: ["troubleshooting", "observability", "diagnosis"],
          examples: ["分析服务响应超时的根本原因"],
        },
      ],
      defaultInputModes: ["text", "structured"],
      defaultOutputModes: ["text", "structured", "streaming"],
      authentication: { schemes: ["bearer_token"], required: true },
      security: { tlsRequired: true, rbacRoles: ["admin", "operator", "viewer"] },
      slo: {
        latency: { p50: "500ms", p95: "2s", p99: "5s" },
        availability: "99.9%",
        errorRate: "<0.5%",
      },
    };
  }

  async executeTask(task: AgentTask): Promise<AgentTaskResult> {
    const startTime = performance.now();
    this.audit("task_start", "success", { taskId: task.id });

    try {
      // 调用 AI 服务
      const result = await callAIStream({
        providerId: "zhipu",
        model: "glm-6",
        messages: [
          { role: "system", content: this.buildSystemPrompt() },
          { role: "user", content: JSON.stringify(task.input) },
        ],
        temperature: 0.3,
        stream: false,
      });

      const endTime = performance.now();

      return {
        taskId: task.id,
        status: "completed",
        output: { analysis: result.text },
        metrics: {
          duration: Math.round(endTime - startTime),
          tokenUsage: result.tokenUsage || { prompt: 0, completion: 0, total: 0 },
          startTime,
          endTime,
        },
      };
    } catch (error) {
      this.audit("task_error", "failure", { taskId: task.id, error: String(error) });
      return {
        taskId: task.id,
        status: "failed",
        error: {
          code: "EXECUTION_ERROR",
          message: error instanceof Error ? error.message : String(error),
          retryable: true,
        },
        metrics: {
          duration: Math.round(performance.now() - startTime),
          tokenUsage: { prompt: 0, completion: 0, total: 0 },
          startTime,
          endTime: performance.now(),
        },
      };
    }
  }

  async executeTaskStream(
    task: AgentTask,
    onChunk: (chunk: string) => void
  ): Promise<AgentTaskResult> {
    // 流式实现...
    return this.executeTask(task);
  }

  async healthCheck(): Promise<{ status: "healthy" | "degraded" | "unhealthy" }> {
    return { status: "healthy" };
  }

  private buildSystemPrompt(): string {
    return `你是语枢万物(Thinker)，YYC³ AI Family的思考者。你擅长数据分析与统计建模...`;
  }
}
```

---

## 三、MCP Client 实现参考

### 3.1 API 契约

```typescript
// src/app/lib/mcp-client.ts
export interface MCPToolDefinition {
  name: string;
  description: string;
  inputSchema: Record<string, unknown>;
}

export interface MCPToolCall {
  name: string;
  arguments: Record<string, unknown>;
}

export interface MCPToolResult {
  content: Array<{
    type: "text" | "image" | "resource";
    text?: string;
    data?: string;
    mimeType?: string;
  }>;
  isError?: boolean;
}

export interface MCPClientOptions {
  serverUrl: string;
  transport: "stdio" | "streamable-http";
  timeout?: number;
  retryCount?: number;
  correlationId?: string;
}

export class MCPClient {
  private options: MCPClientOptions;

  constructor(options: MCPClientOptions) {
    this.options = {
      timeout: 30000,
      retryCount: 3,
      ...options,
    };
  }

  /** 发现可用工具 */
  async listTools(): Promise<MCPToolDefinition[]>;

  /** 调用工具 */
  async callTool(toolCall: MCPToolCall): Promise<MCPToolResult>;

  /** 列出可用资源 */
  async listResources(): Promise<Array<{ uri: string; name: string }>>;

  /** 读取资源 */
  async readResource(uri: string): Promise<string>;

  /** 断开连接 */
  async disconnect(): Promise<void>;
}
```

### 3.2 测试用例

```typescript
// src/app/__tests__/mcp-client.test.ts
import { describe, it, expect, vi, beforeEach } from "vitest";
import { MCPClient } from "../lib/mcp-client";

describe("MCPClient", () => {
  let client: MCPClient;

  beforeEach(() => {
    client = new MCPClient({
      serverUrl: "http://localhost:3001",
      transport: "streamable-http",
    });
  });

  it("应成功列出工具", async () => {
    const tools = await client.listTools();
    expect(Array.isArray(tools)).toBe(true);
    expect(tools.length).toBeGreaterThan(0);
    expect(tools[0]).toHaveProperty("name");
    expect(tools[0]).toHaveProperty("description");
    expect(tools[0]).toHaveProperty("inputSchema");
  });

  it("应成功调用工具", async () => {
    const result = await client.callTool({
      name: "query",
      arguments: { sql: "SELECT 1" },
    });
    expect(result).toHaveProperty("content");
    expect(result.isError).toBe(false);
  });

  it("应处理工具调用失败", async () => {
    await expect(
      client.callTool({
        name: "non_existent_tool",
        arguments: {},
      })
    ).rejects.toThrow();
  });

  it("应支持重试机制", async () => {
    // 测试重试逻辑
  });
});
```

---

## 四、A2A Client 实现参考

### 4.1 API 契约

```typescript
// src/app/lib/a2a-client.ts
export interface A2ATaskState {
  taskId: string;
  status: "submitted" | "working" | "completed" | "failed" | "cancelled";
  message?: string;
  artifacts?: Array<{
    name: string;
    parts: Array<{ text?: string; data?: Record<string, unknown> }>;
  }>;
}

export interface A2AClientOptions {
  baseUrl: string;
  timeout?: number;
  correlationId?: string;
}

export class A2AClient {
  private options: A2AClientOptions;

  constructor(options: A2AClientOptions);

  /** 获取远程Agent的Agent Card */
  async getAgentCard(): Promise<AgentCard>;

  /** 发送任务委托 */
  async sendTask(
    task: AgentTask,
    onStateChange?: (state: A2ATaskState) => void
  ): Promise<AgentTaskResult>;

  /** 取消任务 */
  async cancelTask(taskId: string): Promise<void>;

  /** 获取任务状态 */
  async getTaskStatus(taskId: string): Promise<A2ATaskState>;
}
```

---

## 五、内容安全过滤实现参考

### 5.1 API 契约

```typescript
// src/app/lib/content-filter.ts
export type RiskLevel = "none" | "low" | "medium" | "high" | "critical";

export type ContentCategory =
  | "political"
  | "pornography"
  | "violence"
  | "data_leak"
  | "jailbreak"
  | "bias"
  | "commercial_sensitive"
  | "copyright"
  | "high_risk_advice"
  | "offensive_language";

export interface FilterResult {
  safe: boolean;
  riskLevel: RiskLevel;
  categories: ContentCategory[];
  confidence: number;
  reason?: string;
  action: "allow" | "block" | "flag" | "sanitize" | "review";
  sanitizedContent?: string;
}

export interface ContentFilterOptions {
  strictness: "strict" | "moderate" | "relaxed";
  customPatterns?: RegExp[];
  enableML: boolean;
}

export class ContentFilter {
  constructor(options: ContentFilterOptions);

  /** 输入过滤 */
  async filterInput(input: string): Promise<FilterResult>;

  /** 输出过滤 */
  async filterOutput(output: string): Promise<FilterResult>;

  /** 更新过滤规则 */
  updateRules(rules: ContentFilterOptions): void;
}
```

---

## 六、提示词注入检测实现参考

### 6.1 API 契约

```typescript
// src/app/lib/injection-detector.ts
export type AttackType =
  | "direct_injection"
  | "indirect_injection"
  | "multi_turn"
  | "encoding"
  | "roleplay"
  | "context_hijacking"
  | "multilingual"
  | "tool_injection";

export interface InjectionResult {
  safe: boolean;
  riskLevel: "none" | "low" | "medium" | "high" | "critical";
  attackType?: AttackType;
  confidence: number;
  reason?: string;
  action: "allow" | "block" | "flag" | "review";
}

export class InjectionDetector {
  /** 检测用户输入是否包含注入攻击 */
  async detect(input: string, context?: {
    history?: string[];
    systemPrompt?: string;
  }): Promise<InjectionResult>;

  /** 对输入进行安全清洗 */
  sanitize(input: string): string;
}
```

---

## 七、部署方案

### 7.1 Docker Compose 开发环境

```yaml
# docker-compose.dev.yml
version: "3.8"
services:
  yyc3-app:
    build:
      context: .
      dockerfile: Dockerfile.dev
    ports:
      - "21001:3000"  # 前端端口 (20000-24999区间)
    environment:
      - NODE_ENV=development
      - DATABASE_URL=postgresql://yyc3:yyc3@postgres:5432/yyc3
    volumes:
      - ./src:/app/src
    depends_on:
      - postgres
      - redis

  postgres:
    image: pgvector/pgvector:pg16
    ports:
      - "25432:5432"
    environment:
      POSTGRES_USER: yyc3
      POSTGRES_PASSWORD: yyc3
      POSTGRES_DB: yyc3
    volumes:
      - pgdata:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "26379:6379"

  prometheus:
    image: prom/prometheus
    ports:
      - "30901:9090"  # 中间件端口 (30000-34999区间)
    volumes:
      - ./config/prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana
    ports:
      - "30902:3000"

  jaeger:
    image: jaegertracing/all-in-one
    ports:
      - "30910:16686"  # UI
      - "30911:4317"   # OTLP gRPC

volumes:
  pgdata:
```

### 7.2 生产环境 K8s 部署

```yaml
# k8s/production/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: yyc3-agent-deployment
  labels:
    app: yyc3-agent
    version: v2.1.0
spec:
  replicas: 3
  selector:
    matchLabels:
      app: yyc3-agent
  template:
    metadata:
      labels:
        app: yyc3-agent
        version: v2.1.0
    spec:
      containers:
        - name: yyc3-agent
          image: yyc3/agent:latest
          ports:
            - containerPort: 3000
          env:
            - name: NODE_ENV
              value: "production"
            - name: OTEL_EXPORTER_OTLP_ENDPOINT
              value: "http://jaeger:4317"
          resources:
            requests:
              memory: "512Mi"
              cpu: "500m"
            limits:
              memory: "2Gi"
              cpu: "2000m"
          livenessProbe:
            httpGet:
              path: /api/health
              port: 3000
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /api/ready
              port: 3000
            initialDelaySeconds: 5
            periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: yyc3-agent-service
spec:
  type: LoadBalancer
  selector:
    app: yyc3-agent
  ports:
    - port: 443
      targetPort: 3000
      protocol: TCP
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: yyc3-agent-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: yyc3-agent-deployment
  minReplicas: 3
  maxReplicas: 20
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
```

### 7.3 端口分配方案

根据用户端口分配规则：

| 服务 | 端口 | 区间 | 含义 |
|------|------|------|------|
| YYC³ 前端 | 21001 | 20000-24999 | 大类21(Web), 模块01, 实例1 |
| YYC³ API | 25301 | 25000-29999 | 大类25(API), 模块01, 实例1 |
| PostgreSQL | 25432 | 25000-29999 | 数据库端口映射 |
| Redis | 26379 | 25000-29999 | 缓存端口映射 |
| MCP Server | 30201 | 30000-34999 | 大类30(协议), 模块01, 实例1 |
| A2A Server | 30202 | 30000-34999 | 大类30(协议), 模块02, 实例1 |
| Prometheus | 30901 | 30000-34999 | 监控端口 |
| Grafana | 30902 | 30000-34999 | 可视化端口 |
| Jaeger | 30910-30911 | 30000-34999 | 链路追踪端口 |
| AI 模型服务 | 40101 | 40000-44999 | 大类40(AI), 模块01, 实例1 |

---

## 变更历史

| 版本 | 日期 | 变更内容 | 作者 |
|------|------|---------|------|
| v1.0.0 | 2026-06-03 | 初始版本，工程实现参考手册 | YanYuCloudCube Team |

---

<div align="center">

> 「***YanYuCloudCube***」
> 「***<admin@0379.email>***」
> ***Words Initiate Quadrants, Language Serves as Core for the Future***

**© 2025-2026 YYC³ Team. All Rights Reserved.**
</div>