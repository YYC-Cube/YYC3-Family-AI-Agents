# 贡献指南（CONTRIBUTING）

> ***YanYuCloudCube*** · *言启象限 | 语枢未来*
> 感谢你为 YYC³ AI Family 贡献力量！请先阅读本指南与 [行为准则](CODE_OF_CONDUCT.md)。

---

## 🚀 快速开始

### 环境准备

```bash
# 1. 克隆仓库
git clone git@github.com:YYC-Cube/YYC3-Family-AI-Agents.git
cd YYC3-Family-AI-Agents

# 2. 安装运行时依赖（Python 3.12+）
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 3. 一键生产部署（N2 DGX Spark，可选）
bash deploy/install.sh
bash deploy/verify.sh          # 全链路验证
```

### 本地运行（端口 3030 起 🚨）

```bash
python3 agent_server.py                     # 单 Agent 服务
python3 governance_hub.py                   # 治理中枢仪表盘
# 或容器化
docker compose up -d
```

---

## 📁 仓库结构约定

| 路径 | 用途 | 变更约束 |
| ---- | ---- | ---- |
| `agent_server.py` / `governance_hub.py` | 生产运行时（Flask） | 需通过语法检查 + 冒烟测试 |
| `agents/<name>/` | 家人身份/灵魂/系统提示 | 名称变更需跨层同步（README + docs + deploy） |
| `deploy/` | 生产部署与 systemd | 未经生产验证不得合并 |
| `docs/` | 全部文档（编号体系见下） | 遵循文档规范 |
| `examples/` | 示例代码（蓝图原型） | 不接入生产，仅作实现参考 |
| `public/` | 品牌素材 | 需与品牌规范一致 |

### docs/ 编号体系

```
docs/
├── README.md                        ← 文档总导航
├── 0379-family-ai-agents-*/         ← 会话工作目录（审核/规划/日志/总结，按 YYC³ 协同规范）
├── 10-YYC3-提示词工程-企业蓝图/      ← 提示词工程蓝图（1200-1213 编号体系）
└── YYC3-*-编程体系|企业蓝图/         ← 双维度体系文档
```

> 新增顶层专题请使用两位编号前缀（如 `11-`），保持可排序性；会话目录命名遵循 `{项目}-{导师}-{YYYYMMDD}`。

---

## 🔄 开发工作流（PDCA+）

遵循 YYC³ 团队《AI 协同开发文档》规范：

1. **Plan**：明确目标与验收标准，重大变更先在 `docs/{会话目录}/01-任务规划与节点目标.md` 立项
2. **Do**：小步提交，每个 commit 聚焦一件事
3. **Check**：提交前自检（见下方质量门禁）
4. **Act**：不通过则修复，通过则更新执行日志
5. **Archive**：会话结束生成总结文档，为衔接留上下文

### 提交信息规范（Conventional Commits）

```
<type>(<scope>): <subject>

[body: 为什么改，而非改了什么]
```

- type：`feat` / `fix` / `docs` / `refactor` / `chore` / `test` / `deploy`
- scope：`agents` / `hub` / `server` / `docs` / `deploy` / `examples`
- 示例：`docs(12/13): P0 一致性修复 — 命名归一千里·伯乐 + README 索引校正`

### 版本与标签

- 版本号遵循 [SemVer](https://semver.org/lang/zh-CN/)，变更记录写入 [CHANGELOG.md](CHANGELOG.md)
- 发布时打三类标签：`vX.Y.Z` + `component/<组件>-vX.Y.Z` + `milestone/<里程碑>`
- 未经仓库所有者指示，不执行 `git push --force`，不直接推送 main 之外的保护分支

---

## ✅ 质量门禁

提交前必须全部通过：

| 检查项 | 命令 | 标准 |
| ---- | ---- | ---- |
| Python 语法 | `python3 -m py_compile agent_server.py governance_hub.py` | 0 error |
| 依赖安装 | `pip install -r requirements.txt` | 无冲突 |
| 服务冒烟 | `python3 agent_server.py` 后 `curl :25600/health` | 200 |
| 文档链接 | 检查本次改动 md 内相对链接可达 | 无死链 |
| 敏感信息 | 不硬编码密钥/Token，`.env` 不入库 | git status 干净 |

---

## 📝 文档贡献规范

- 所有 md 文档遵循 YYC³ 品牌标头（人从众曌众从人 / 家训 / 使命）与标尾签名
- YAML Front Matter 必填：`file` / `description` / `version` / `created` / `status`
- 引用代码位置使用可点击链接：`[文件](file:///绝对路径#L123-L145)` 或仓库相对路径
- 术语与《家人命名注册表》一致（如「千里·伯乐」，禁用历史旧称「知遇·伯乐」）
- 敏感信息使用占位符：`${ENV_VAR}` 或 `[REDACTED]`

---

## 🆘 需要帮助

- 问题反馈：[GitHub Issues](https://github.com/YYC-Cube/YYC3-Family-AI-Agents/issues)
- 联系邮箱：<admin@0379.email>

> 「***YanYuCloudCube***」 · **© 2025-2026 YanYuCloudCube™. All Rights Reserved.**
