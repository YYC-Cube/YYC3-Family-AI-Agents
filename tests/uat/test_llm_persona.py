"""UAT LLM 实答人设抽检（P2-4）— 环境门控

默认 SKIP：仅当 YYC3_UAT_LLM=1 且 vLLM 端点可达时才真实执行（部署后验收用）。
运行: YYC3_UAT_LLM=1 .venv/bin/python -m pytest tests/uat/test_llm_persona.py -v
"""
import os
import sys
import urllib.request
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

ENABLED = os.environ.get("YYC3_UAT_LLM") == "1"
VLLM_BASE = os.environ.get("VLLM_ENDPOINT", "http://localhost:8000/v1")
VLLM_MODEL = os.environ.get("VLLM_MODEL", "Qwen/Qwen3.6-27B-FP8")

pytestmark = pytest.mark.skipif(not ENABLED, reason="需 YYC3_UAT_LLM=1 且生产 vLLM 可达（部署后验收）")

# 抽检矩阵：短名 → (身份问题, 答案必须包含的关键词)
PROBES = {
    "tianshu": ("你是谁？你的角色是什么？", ["元启", "天枢", "总指挥"]),
    "qianxing": ("你是谁？你的角色是什么？", ["言启", "千行", "导航"]),
    "wanwu": ("你是谁？你的角色是什么？", ["语枢", "万物"]),
    "xianzhi": ("你是谁？你的角色是什么？", ["预见", "先知"]),
    "bole": ("你是谁？你的角色是什么？", ["千里", "伯乐", "推荐"]),
    "shouhu": ("你是谁？你的角色是什么？", ["智云", "守护"]),
    "zongshi": ("你是谁？你的角色是什么？", ["格物", "宗师"]),
    "lingyun": ("你是谁？你的角色是什么？", ["创想", "灵韵"]),
}


def _vllm_reachable() -> bool:
    try:
        with urllib.request.urlopen(f"{VLLM_BASE}/models", timeout=3) as r:
            return r.status == 200
    except Exception:
        return False


def _chat(system: str, user: str) -> str:
    import requests
    resp = requests.post(f"{VLLM_BASE}/chat/completions",
                         json={"model": VLLM_MODEL, "messages": [
                             {"role": "system", "content": system},
                             {"role": "user", "content": user},
                         ], "temperature": 0.1, "max_tokens": 256, "stream": False,
                             "chat_template_kwargs": {"enable_thinking": False}},
                         timeout=60)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


@pytest.mark.parametrize("short", sorted(PROBES.keys()))
def test_persona_identity_answer(short):
    if not _vllm_reachable():
        pytest.skip(f"vLLM 不可达: {VLLM_BASE}")
    system = (REPO_ROOT / "agents" / {
        "tianshu": "yuanqi-tianshu", "qianxing": "yanqi-qianhang",
        "wanwu": "yushu-wanwu", "xianzhi": "yujian-xianzhi", "bole": "zhiyu-bole",
        "shouhu": "zhiyun-shouhu", "zongshi": "gewu-zongshi", "lingyun": "chuangxiang-lingyun",
    }[short] / "SYSTEM.md").read_text(encoding="utf-8")
    question, keywords = PROBES[short]
    answer = _chat(system, question)
    assert answer, "LLM 返回空回答"
    hit = [k for k in keywords if k in answer]
    assert hit, f"人设漂移：回答未命中任何关键词 {keywords}，实际回答: {answer[:200]}"
