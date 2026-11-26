# Hooks · 注入检测

`guardrails_hook.py`：PreToolUse 注入检测脚本（与产线 `guardrails.py` 同一规则引擎）。

- **输入**：stdin JSON（宿主 PreToolUse 事件，含 `tool_name` / `tool_input`）
- **行为**：抽取最大文本字段 → `inspect_input` → `verdict==block` 时输出 `{"decision":"block","reason":...}`
- **注册**：依宿主 spec 在 hooks 配置中将 PreToolUse 指向 `python3 .claude-plugin/hooks/guardrails_hook.py`（不同宿主接线格式以其官方文档为准，本插件不自带宿主私有格式）

> 降级语义：护栏自身异常时静默放行（不阻塞工具面）；拦截/放行的产线级审计由治理中枢审计链承担。
