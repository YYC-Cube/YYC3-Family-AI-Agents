"""W2-B 插件件套契约测试 — .claude-plugin/ 结构（Skills/Agents/Commands/Hooks/MCP 五位一体）

零 LLM 依赖、离线可跑、随 CI 全量门禁。守护四件套完整性与命名统一（8 英文 id）。
"""
import json
import re
from pathlib import Path

PLUGIN_DIR = Path(__file__).resolve().parents[2] / ".claude-plugin"
AGENTS_DIR = Path(__file__).resolve().parents[2] / "agents"
EXPECTED_IDS = {
    "meta-oracle", "navigator", "thinker", "prophet",
    "bolero", "sentinel", "master", "creative",
}


def test_plugin_manifest_valid():
    data = json.loads((PLUGIN_DIR / "plugin.json").read_text(encoding="utf-8"))
    assert data["name"] == "yyc3-family-ai"
    assert data["version"] == "3.1.0"
    assert {Path(p).stem for p in data["skills"]} == EXPECTED_IDS
    assert {Path(p).stem for p in data["agents"]} == EXPECTED_IDS
    assert {Path(p).name for p in data["commands"]} == {"audit.md", "budget.md", "freeze.md"}


def test_skills_frontmatter_ids():
    for sid in EXPECTED_IDS:
        text = (PLUGIN_DIR / "skills" / f"{sid}.md").read_text(encoding="utf-8")
        m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
        assert m, f"skills/{sid}.md 缺 frontmatter"
        assert f"name: {sid}" in m.group(1)
        assert "description:" in m.group(1)


def test_subagent_definitions_frontmatter():
    for sid in EXPECTED_IDS:
        text = (PLUGIN_DIR / "agents" / f"{sid}.md").read_text(encoding="utf-8")
        m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
        assert m, f"agents/{sid}.md 缺 frontmatter（非 ZCode subagent 格式）"
        assert f"name: {sid}" in m.group(1)
        assert "SYSTEM.md" in text  # 运行时人格权威源指针


def test_commands_have_frontmatter():
    for cmd in ("audit.md", "budget.md", "freeze.md"):
        text = (PLUGIN_DIR / "commands" / cmd).read_text(encoding="utf-8")
        assert text.startswith("---") and "name:" in text


def test_mcp_config_points_to_governance_hub():
    for f in (".mcp.json", "plugin.json"):
        cfg = json.loads((PLUGIN_DIR / f).read_text(encoding="utf-8"))
        s = json.dumps(cfg)
        assert ":25700/mcp" in s, f"{f} 未指向治理中枢 /mcp"
        assert "${YYC3_MCP_KEY}" in s, f"{f} 密钥未走环境变量（禁硬编码）"


def test_hook_uses_production_guardrails_engine():
    hook = (PLUGIN_DIR / "hooks" / "guardrails_hook.py").read_text(encoding="utf-8")
    assert "inspect_input" in hook  # 与产线 /chat 同一规则引擎
    assert "decision" in hook and "block" in hook


def test_skill_ids_align_with_runtime_agents_dirs():
    runtime_dirs = {p.name for p in AGENTS_DIR.iterdir() if p.is_dir()}
    assert runtime_dirs == EXPECTED_IDS
