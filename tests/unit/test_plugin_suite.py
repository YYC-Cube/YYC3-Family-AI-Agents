"""W2-B 插件件套契约测试 — .claude-plugin/ 结构（Skills/Agents/Commands/Hooks/MCP 五位一体）

零 LLM 依赖、离线可跑、随 CI 全量门禁。
v3（2026-11-26）：Skills 升级为开源标准目录式（SKILL.md + references/persona.md 渐进披露），
新增「技能库 ↔ agents/ 运行时人格」跨文件对齐门禁（座右铭逐字对齐 SOUL）。
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PLUGIN_DIR = ROOT / ".claude-plugin"
AGENTS_DIR = ROOT / "agents"
EXPECTED_IDS = {
    "meta-oracle", "navigator", "thinker", "prophet",
    "bolero", "sentinel", "master", "creative",
}


def test_plugin_manifest_valid():
    data = json.loads((PLUGIN_DIR / "plugin.json").read_text(encoding="utf-8"))
    assert data["name"] == "yyc3-family-ai"
    assert data["version"] == "3.1.0"
    assert {Path(p).parent.name for p in data["skills"]} == EXPECTED_IDS
    assert all(p.endswith("SKILL.md") for p in data["skills"]), "skills 须为目录式 SKILL.md 路径"
    assert {Path(p).stem for p in data["agents"]} == EXPECTED_IDS
    assert {Path(p).name for p in data["commands"]} == {"audit.md", "budget.md", "freeze.md"}


def test_skills_directory_form_and_frontmatter():
    for sid in EXPECTED_IDS:
        skill_md = PLUGIN_DIR / "skills" / sid / "SKILL.md"
        text = skill_md.read_text(encoding="utf-8")
        m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
        assert m, f"skills/{sid}/SKILL.md 缺 frontmatter"
        assert f"name: {sid}" in m.group(1)
        assert "description:" in m.group(1)
        # 渐进披露：references/persona.md 存在且被 SKILL.md 指引
        assert (PLUGIN_DIR / "skills" / sid / "references" / "persona.md").exists()
        assert "references/persona.md" in text
        # 运行时人格权威源指针
        assert f"agents/{sid}/" in text


def test_skills_aligned_with_agents_soul_motto():
    """全量对齐门禁：references/persona.md 的座右铭必须与 agents/<id>/SOUL.md 逐字一致"""
    for sid in EXPECTED_IDS:
        soul = (AGENTS_DIR / sid / "SOUL.md").read_text(encoding="utf-8")
        m = re.search(r"\*\*座右铭\*\*: (.+)", soul)
        assert m, f"agents/{sid}/SOUL.md 缺座右铭行"
        motto = m.group(1).strip()
        persona = (PLUGIN_DIR / "skills" / sid / "references" / "persona.md").read_text(encoding="utf-8")
        assert motto in persona, f"skills/{sid}/references/persona.md 座右铭与 SOUL 不一致"


def test_skills_declare_global_dedicated_skills():
    """对齐全局家族清单：每成员声明 4 个版本化专属技能（<id>.<skill> 形态）"""
    for sid in EXPECTED_IDS:
        text = (PLUGIN_DIR / "skills" / sid / "SKILL.md").read_text(encoding="utf-8")
        declared = set(re.findall(rf"`{sid}\.([a-z-]+)`（v", text))
        assert len(declared) == 4, f"{sid} 专属技能应为 4 个，实得 {declared}"


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
