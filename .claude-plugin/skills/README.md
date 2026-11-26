# Skills 库 · 8 位家人技能（对齐 agents/ 运行时人格）

> 结构对齐开源 Agent Skills 标准（文件夹式 `SKILL.md` + `references/` 渐进披露；格式已捐赠 Agentic AI Foundation 开放标准）＋ 全局家族清单模式（每成员 4 个版本化专属技能，SSOT: family-manifest）。
> **人格单一事实源 = `agents/<id>/{IDENTITY,SOUL,SYSTEM}.md`**——本库为派生视图（人格精要在各 `references/persona.md`），不手改权威内容。

## 对齐矩阵

| id | 名号 | 角色 | 端口 | 专属技能（×4） | golden 锚点 |
|---|---|---|---|---|---|
| meta-oracle | 元启·天枢 | 总指挥 | :25600 | task-decomposition · strategy-orchestration · global-oversight · conflict-arbitration | identity/domain/boundary/**unreachable** |
| navigator | 言启·千行 | 导航员 | :25601 | intent-detection · ambiguity-clarify · nlq-to-api · context-session | identity/domain/boundary/**unreachable** |
| thinker | 语枢·万物 | 思考者 | :25602 | business-analysis · root-cause · report-compose · decision-support | identity/domain/boundary/**unreachable** |
| prophet | 预见·先知 | 预言家 | :25603 | trend-forecast · risk-alert · scenario-simulate · capacity-forecast | identity/domain/boundary |
| bolero | 知遇·伯乐 | 推荐官 | :25604 | talent-match · persona-profile · personalize · achievement-insight | identity/domain/boundary/**unreachable** |
| sentinel | 智云·守护 | 安全官 | :25605 | security-audit · zero-trust · content-filter · incident-response | identity/domain/boundary |
| master | 格物·宗师 | 质量官 | :25606 | quality-gate · regression-guard · knowledge-distill · retrospective | identity/domain/boundary |
| creative | 创想·灵韵 | 创意官 | :25607 | ideation · copywriting · marketing-content · style-direction | identity/domain/boundary |

## 目录结构（每成员）

```
skills/<id>/
├── SKILL.md                  ← 入口（触发/专属技能/框架/输出契约/协作协议/治理约束）
└── references/
    └── persona.md            ← 人格精要（座右铭/五维职能全表/行为约束/协同家族/家族誓言——派生自 agents/<id>/SOUL）
```

## 对齐纪律

1. 权威源唯一：`agents/<id>/` 三件套；本库任何冲突以三件套为准。
2. 座右铭/五维职能/行为约束/誓言 由契约测试与 SOUL 跨文件对齐（`tests/unit/test_plugin_suite.py`）。
3. 委托一律走产线 `/delegate`（深度 ≤2），诚实红线：未经通道返回严禁声称已委派/已完成。
