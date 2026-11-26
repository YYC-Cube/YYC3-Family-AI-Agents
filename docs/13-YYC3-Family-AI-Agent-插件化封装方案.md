---
file: "13-YYC3-Family-AI-Agent-插件化封装方案.md"
title: "YYC³ FAmily-AI Agent · 插件化封装方案（教科书级）"
description: "基于 2025-2026 开源生态对标（LangGraph/CrewAI/MCP/Claude Code Plugins），将本仓封装为即插即用的插件/Skills/本地开发包——三条路径 × 五步落地 × 生产检查清单"
author: "YanYuCloudCube Team <admin@0379.email>"
version: "v1.0.0"
created: "2026-11-02"
updated: "2026-11-02"
status: "active"
license: "MIT"
---

# YYC³ FAmily-AI Agent · 插件化封装方案

> ***YanYuCloudCube*** · *言启象限 | 语枢未来*
> *封装即分发，即插即用是生产落地的最后一公里。*

---

## 0. 文档定位 | Purpose

本仓已具备完整的多智能体治理能力（审计链/预算/Kill Switch/护栏/语义记忆/持久化执行/MCP/A2A）。本文回答：**如何将这套能力封装为便捷可用的插件/Skills/本地开发包**，让外部消费者零配置接入。

Three packaging tracks: **A. MCP Server** (protocol-first) · **B. Claude Code Plugin** (skill-first) · **C. pip Package** (code-first).

---

## 1. 生态对标 | Ecosystem Benchmark

### 1.1 编排框架封装范式

| 框架 | 封装单元 | 分发方式 | 即插即用程度 |
|---|---|---|---|
| LangGraph | Graph（图编排） | pip install langgraph · LangSmith Deployment | ★★★☆☆ 需编写图定义 |
| CrewAI | Crew（角色团队） | pip install crewai · YAML 配置驱动 | ★★★★☆ 配置即用 |
| OpenAI Agents SDK | Agent（五原语） | pip install openai-agents · MCP 接入 | ★★★★★ 五原语即用 |
| Claude Code | Plugin（skill+hook+MCP） | /plugin install @marketplace | ★★★★★ 一键安装 |
| Google ADK | Agent（多语言） | pip install google-adk | ★★★☆☆ GCP 绑定 |

**行业共识**：封装单元从"代码库"收敛为"**plugin = skills + hooks + MCP servers 的可分发包**"。

### 1.2 MCP 生态封装范式

| 模式 | 说明 | 本仓对位 |
|---|---|---|
| MCP Server | 暴露工具/资源/提示词（streamable HTTP / stdio） | governance_hub `/mcp` 端点（已实现） |
| MCP Registry | 中央注册表发现服务 | 预留（E2-1 后续） |
| Claude Code Plugin | `.claude/` 目录捆绑 skills/commands/hooks/MCP | **E3-2 封装目标** |

### 1.3 本仓独有差异化资产

| 资产 | 生态稀缺度 | 封装价值 |
|---|---|---|
| 审计链（全程上报 + correlation_id 贯穿，SQLite 追加写） | **稀缺**——框架普遍无审计 | 核心卖点（2026-11-26 审核勘误：原表述「FNV-1a 链式哈希防篡改」与本仓代码不符，链式哈希属兄弟仓 kernel 资产待验证，见 docs/14- §8.2④） |
| Token 预算窗口（日/周/月惰性重置） | 稀缺 | 核心卖点 |
| Kill Switch（一键冻结） | 稀缺 | 核心卖点 |
| 护栏管线（注入检测 + 输出脱敏） | 有（NeMo Guardrails 等） | 差异化：零依赖 + 审计闭环 |
| 分层记忆 Semantic 首批 | 有（Mem0/Zep） | 同层竞品 |
| 语义层 MDL（WrenAI 形态） | 有（WrenAI 首创） | 差异化：中文场景 + 治理闭环 |

---

## 2. 封装路径 | Three Tracks

### 路径 A：MCP Server（协议优先）

**定位**：将治理中枢能力暴露为标准 MCP 工具，任何支持 MCP 的框架/客户端可即插即用。

```
消费者（LangGraph / CrewAI / Claude / 任意 MCP host）
    ↕ JSON-RPC 2.0 (streamable HTTP, 2026-07-28 stateless)
治理中枢 /mcp 端点
    ├── governance_budget_overview     （预算仪表盘）
    ├── governance_audit_search        （审计检索）
    ├── governance_agent_states        （家人状态）
    └── [后续] memory_semantic_recall  （语义记忆召回）
```

**实现要点**：
- 已有 `POST /mcp` 端点（stateless JSON-RPC 2.0，对齐 2026-07-28 子集）
- 零信任鉴权（X-API-Key）+ 审计链（tools/call 入审计）
- 无 session 粘滞 → 天然水平扩缩

**消费者接入**（零配置——只填 URL 和 Key）：

```python
# 任意 MCP host（Claude Code / LangGraph / 自研）
mcp_client = McpClient("http://hub:25700/mcp", api_key=os.environ["YYC3_MCP_KEY"])
result = mcp_client.tools_call("governance_budget_overview")
```

### 路径 B：Claude Code Plugin（Skill 优先）

**定位**：将 8 位家人能力封装为 Claude Code 可发现的 Plugin（skills/commands/hooks/MCP）。

```
.claude-plugin/
├── plugin.json          ← Plugin 元数据（name/version/skills/commands）
├── skills/
│   ├── meta-oracle.md       ← 元启·天枢 Skill（决策框架+治理约束）
│   ├── navigator.md      ← 言启·千行 Skill（需求转译+路由）
│   ├── thinker.md         ← 语枢·万物 Skill（经营分析+边界红线）
│   └── ...
├── commands/
│   ├── audit.md         ← /audit 命令（查审计链）
│   ├── budget.md        ← /budget 命令（查预算）
│   └── freeze.md        ← /freeze 命令（Kill Switch）
├── hooks/
│   └── guardrails.py    ← 输入注入检测 hook（PreToolUse）
└── .mcp.json            ← MCP server 引用（治理中枢 /mcp）
```

**消费者接入**（一行命令）：
```bash
claude plugin add github:YYC-Cube/YYC3-Family-AI-Agents
```

### 路径 C：pip Package（代码优先）

**定位**：将核心模块（护栏管线/语义层/持久化执行/学习闭环）封装为 pip 可安装包。

```
yyc3-family-ai/
├── pyproject.toml       ← setuptools 配置（entry_points 定义 CLI）
├── src/
│   └── yyc3_family/
│       ├── __init__.py
│       ├── guardrails.py       ← 注入检测 + 输出脱敏
│       ├── semantic_layer.py   ← MDL 建模 + SQL 治理管线
│       ├── memory_semantic.py  ← 语义事实记忆
│       ├── durable.py          ← 持久化执行 checkpoint
│       └── cli.py              ← CLI 入口（yyc3-chat / yyc3-audit / yyc3-mdl）
└── tests/
```

**消费者接入**（两行代码）：
```python
from yyc3_family import Guardrails, SemanticLayer
guard = Guardrails.from_mdl("mdl/demo.mdl.yaml")
result = guard.inspect_input("用户问题")
```

---

## 3. 三路径对比 | Track Comparison

| 维度 | A. MCP Server | B. Claude Code Plugin | C. pip Package |
|---|---|---|---|
| 消费者 | 任意 MCP host | Claude Code 用户 | Python 开发者 |
| 接口 | JSON-RPC 2.0 (HTTP) | skill/命令 + hook | Python API + CLI |
| 即插即用 | ★★★★★ 填 URL 即用 | ★★★★☆ 安装后可用 | ★★★☆☆ pip install + 导入 |
| 零依赖 | ✓ hub 侧已零依赖 | ✓ Claude Code 原生 | ✓ 零强制依赖 |
| 审计闭环 | ✓ 全量入审计链 | ✓ hook 事件入审计 | ✓ 调用方可选审计 |
| 部署 | hub 已在运行（25700） | `.claude-plugin/` 目录复制 | pip install yyc3-family |
| 生产状态 | **已实现**（/mcp 端点在线） | 待封装 | 待提取核心模块 |

**推荐**：三路径**并行推进**——A 是已实现的线上服务（立即有用），B 面向 Claude Code 生态（增量最大），C 面向 Python 开发者（复用最广）。

---

## 4. 五步落地路线 | 5-Step Implementation

### Step 1：MCP Server 工具面扩展——✅ 已落地（2026-11-24）

已落地 8 个工具（tools/list 与下表对齐；契约测试 20 passed，全量 318+8 全绿）：

| 工具名 | 功能 | 输入参数 |
|---|---|---|
| `governance_budget_overview` | 预算仪表盘 | （无参数） |
| `governance_audit_search` | 审计检索 | agent?, limit? |
| `governance_agent_states` | 家人状态 | （无参数） |
| `memory_semantic_recall` | 语义记忆召回 | agent, query, top_k? |
| `memory_semantic_store` | 语义事实写入 | agent, text, correlation_id? |
| `guardrails_inspect` | 输入注入检测 | text |
| `semantic_query` | 语义层指标查询 | question |
| `durable_resume` | 断点恢复查询 | correlation_id |

**MVP 文件**：`governance_hub.py` 扩展 MCP_TOOLS 清单 + `_mcp_tool_call` 派发。

### Step 2：Claude Code Plugin 封装（`.claude-plugin/` 目录）

**MVP 文件**：`.claude-plugin/plugin.json` + `skills/meta-oracle.md` + `commands/audit.md`

plugin.json 结构（对齐 Claude Code Plugin spec）：
```json
{
  "name": "yyc3-family-ai",
  "version": "3.1.0",
  "description": "YYC³ FAmily-AI · 1+8 拟人化协同智能体系统",
  "skills": ["skills/meta-oracle.md", "skills/navigator.md", "..."],
  "commands": ["commands/audit.md", "commands/budget.md"],
  "mcpServers": {
    "yyc3-governance": {
      "url": "http://localhost:25700/mcp",
      "headers": {"X-API-Key": "${YYC3_MCP_KEY}"}
    }
  }
}
```

### Step 3：pip 包提取（`pyproject.toml` + src/ 布局）——✅ 骨架已落地（2026-11-24，flat py-modules 形态；src/ 命名空间迁移列后续）

**核心模块**（零强制依赖，全部 stdlib）：
- `yyc3_family.guardrails` — 注入检测 + 输出脱敏（复用 `guardrails.py`）
- `yyc3_family.semantic_layer` — MDL 建模 + 治理管线（复用 `semantic_layer.py`）
- `yyc3_family.memory_semantic` — 语义事实记忆（复用 `memory_semantic.py`）
- `yyc3_family.durable` — 持久化执行 checkpoint（复用 `durable.py`）

**CLI entry_points**：
```toml
[project.scripts]
yyc3-chat = "yyc3_family.cli:chat"
yyc3-audit = "yyc3_family.cli:audit"
yyc3-mdl = "yyc3_family.cli:mdl_validate"
```

### Step 4：发布与分发

| 渠道 | 命令 | 消费者 |
|---|---|---|
| PyPI | `twine upload dist/*` | `pip install yyc3-family-ai` |
| npm（Skill 包） | `npm publish` | Claude Code `/plugin add` |
| GitHub | tag + release | `git clone` + `pip install -e .` |
| Docker Hub | `docker push` | `docker compose up -d` |

### Step 5：文档与生态位

| 产物 | 目标 |
|---|---|
| README.md 安装段 | pip/npm/docker 三行命令 |
| docs/13- | 本文档（封装方案指导） |
| docs/14- | API Reference（自动生成 sphinx-autodoc） |
| PyPI 页面 | README 渲染（long_description = file: README.md） |

---

## 5. 生产落地检查清单 | Production Checklist

- [ ] **pip 包**：`pyproject.toml` 元数据完整（name/version/description/requires-python>=3.12）
- [ ] **MCP server**：`/mcp` 端点通过 zero-trust 鉴权（X-API-Key 必填）
- [ ] **guardrails**：注入样本集拦截率 ≥95%，误杀 ≤2%
- [ ] **semantic memory**：50 事实往返全部命中
- [ ] **durable checkpoint**：断点恢复零 vLLM 调用
- [ ] **CI**：四项检查全绿（语法/依赖/pytest/文档完整性）
- [ ] **PyPI**：`twine check dist/*` 通过，README 渲染正常
- [ ] **npm**：`npm pack --dry-run` 文件清单正确
- [ ] **审计**：全量操作入审计链（correlation_id 贯穿）

---

## 6. 反模式 | Anti-Patterns

| 反模式 | 症状 | 解法 |
|---|---|---|
| **万能插件** | 一个 Plugin 包含所有功能，安装即全量加载 | 按职能拆分：审计 Plugin / 记忆 Plugin / 护栏 Plugin |
| **硬编码密钥** | plugin.json / pyproject.toml 含真实 API Key | 环境变量注入（`${YYC3_MCP_KEY}`）|
| **循环依赖** | Plugin A 依赖 Plugin B 依赖 Plugin A | 依赖仅指向核心层，Plugin 间零依赖 |
| **版本不匹配** | Plugin 版本 ≠ 主仓版本 | 主仓 tag 触发 Plugin 版本同步 |
| **无测试发布** | PyPI 发布未跑 pytest | CI 强制：pytest 绿 → twine upload |
| **文档缺失** | PyPI 页面空白 | long_description = README.md |

---

## 7. 时间线 | Timeline

| 周 | 交付 |
|---|---|
| W1 | 路径 A：MCP server 工具面扩展（8 个工具）**✅ 2026-11-24 落地**（PR #58：tools/list 8 工具 + 每工具契约测试 20 passed；guardrails/semantic/durable 复用 hub 同构函数全链入审计）· 路径 C：pip 包骨架 **✅ 2026-11-24 落地**（`pyproject.toml` + `cli.py`：yyc3-family-ai 3.1.0 零依赖 flat py-modules 打包 5 模块，wheel 真机构建验证 METADATA/entry_points 三入口；yyc3-chat/audit/mdl 可用；`yyc3_family` src/ 命名空间迁移与 PyPI 发布列后续——避免动根模块导入面） |
| W2 | 路径 B：Claude Code Plugin 封装（.claude-plugin/）+ npm 发布 |
| W3 | 路径 C：pip 包 PyPI 发布 + Docker 镜像 + 文档 |
| W4 | 集成测试 + 部署侧验收（PyPI 安装即用验证 / Claude Code 安装验证 / Docker 拉起验证） |

---

## 8. 参考来源 | References

- Claude Code Plugins/Skills/MCP 架构 — [medium.com/24-things](https://medium.com/@meet2sudhakar/24-things-to-add-to-claude-plugins-skills-and-mcp-servers-explained-7cf6a9a8fdcf)
- LangGraph 生产封装 — [github.com/langchain-ai/langgraph](https://github.com/langchain-ai/langgraph)
- CrewAI 角色封装 — [github.com/crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)
- MCP 2026-07-28 规范 — [modelcontextprotocol.io/specification/2026-07-28](https://modelcontextprotocol.io/specification/2026-07-28/changelog)
- Anthropic 构建有效 Agent — [anthropic.com/engineering/building-effective-agents](https://www.anthropic.com/engineering/building-effective-agents)
- 本仓 E1/E2/E3 台账 — [docs/11-演进完善拓展规划](11-YYC3-Family-AI-Agent-演进完善拓展规划.md)

---

> ***YanYuCloudCube***
> *言启象限 | 语枢未来*
> *Words Initiate Quadrants, Language Serves as Core for Future*
> *万象归元于云枢 | 深栈智启新纪元*
