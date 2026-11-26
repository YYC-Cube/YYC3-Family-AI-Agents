#!/usr/bin/env python3
"""YYC³ 插件件套 · PreToolUse 注入检测 hook（docs/13 路径 B / W2）

契约（对齐 docs/13:109 蓝图）：
- stdin 读宿主事件 JSON（{tool_name, tool_input, ...}）；
- 抽取文本参数送 guardrails.inspect_input（与产线 /chat 同一规则引擎：13 条规则，
  high→block / medium→degrade）；
- verdict==block 时输出 {"decision":"block","reason":...}（宿主据此拦截），其余静默放行（exit 0）。
零第三方依赖：仅 stdlib + 仓库根 guardrails 模块（sys.path 定位）。
"""
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from guardrails import inspect_input  # noqa: E402


def _extract_text(tool_input: dict) -> str:
    """抽取工具输入中的最大文本字段（兼容 command/prompt/content/query 等常见键）。"""
    if not isinstance(tool_input, dict):
        return ""
    texts = [v for v in tool_input.values() if isinstance(v, str)]
    return max(texts, key=len) if texts else ""


def main() -> int:
    try:
        event = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        return 0  # Malformed 事件不拦截，交由宿主处理
    text = _extract_text(event.get("tool_input", {}))
    if not text:
        return 0
    try:
        result = inspect_input(text)
    except Exception:
        return 0  # 护栏自身故障不放大数据，也不阻塞工具面（留痕由产线审计链承担）
    if result.get("verdict") == "block":
        print(json.dumps({
            "decision": "block",
            "reason": f"[yyc3-guardrails] 注入规则命中: {result.get('labels')}",
        }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
