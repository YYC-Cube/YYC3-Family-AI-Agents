"""UAT 人设一致性测试（P2-1）

不调用 LLM 的静态人设契约：验证 8 位家人的 IDENTITY.md / SOUL.md / SYSTEM.md
三件套身份一致（名号/角色/座右铭/端口/热线），并抽检 SYSTEM.md 关键人设要素。
LLM 问答抽检依赖真实推理端点，属于部署后验收范畴（tests/uat/README 说明）。
"""
import os
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
AGENTS_DIR = REPO_ROOT / "agents"

# 8 位家人注册表：目录名 → (短名, 中文名号, 家族角色, 端口, 热线)
FAMILY = {
    "yuanqi-tianshu": ("tianshu", "元启·天枢", "总指挥", "25600", "0379-0206"),
    "yanqi-qianhang": ("qianxing", "言启·千行", "导航员", "25601", "0379-0106"),
    "yushu-wanwu": ("wanwu", "语枢·万物", "思考者", "25602", "0379-0107"),
    "yujian-xianzhi": ("xianzhi", "预见·先知", "预言家", "25603", "0379-0108"),
    "zhiyu-bole": ("bole", "千里·伯乐", "推荐官", "25604", "0379-0109"),
    "zhiyun-shouhu": ("shouhu", "智云·守护", "安全官", "25605", "0379-0207"),
    "gewu-zongshi": ("zongshi", "格物·宗师", "质量官", "25606", "0379-0208"),
    "chuangxiang-lingyun": ("lingyun", "创想·灵韵", "创意官", "25607", "0379-0209"),
}


def _identity_table(agent_dir: Path) -> str:
    return (agent_dir / "IDENTITY.md").read_text(encoding="utf-8")


def _soul(agent_dir: Path) -> str:
    return (agent_dir / "SOUL.md").read_text(encoding="utf-8")


def _system(agent_dir: Path) -> str:
    return (agent_dir / "SYSTEM.md").read_text(encoding="utf-8")


@pytest.fixture(params=sorted(FAMILY.keys()), ids=lambda d: FAMILY[d][0])
def family_member(request):
    dirname = request.param
    agent_dir = AGENTS_DIR / dirname
    short, cn_name, role, port, phone = FAMILY[dirname]
    return {
        "dir": agent_dir, "short": short, "cn_name": cn_name,
        "role": role, "port": port, "phone": phone,
        "identity": _identity_table(agent_dir),
        "soul": _soul(agent_dir), "system": _system(agent_dir),
    }


class TestPersonaTripletConsistency:
    """三件套身份一致性：IDENTITY 为权威源，SOUL/SYSTEM 必须与之对齐"""

    def test_triplet_files_exist(self, family_member):
        for f in ("IDENTITY.md", "SOUL.md", "SYSTEM.md"):
            assert (family_member["dir"] / f).exists(), f"缺失 {f}"

    def test_cn_name_consistent_across_triplet(self, family_member):
        name = family_member["cn_name"]
        assert f"| **中文名号** | {name} |" in family_member["identity"]
        assert name in family_member["soul"], "SOUL.md 标题/正文未含权威名号"
        assert name in family_member["system"], "SYSTEM.md 未含权威名号"

    def test_role_consistent(self, family_member):
        assert f"| **家族角色** | {family_member['role']} |" in family_member["identity"]

    def test_motto_consistent_between_identity_and_soul(self, family_member):
        m = re.search(r"\| \*\*座右铭\*\* \| (.+?) \|", family_member["identity"])
        assert m, "IDENTITY.md 缺座右铭行"
        motto = m.group(1).strip()
        assert motto in family_member["soul"], "SOUL.md 座右铭与 IDENTITY 不一致"
        assert motto in family_member["system"], "SYSTEM.md 座右铭与 IDENTITY 不一致"

    def test_port_and_phone_registered(self, family_member):
        assert f":{family_member['port']}" in family_member["identity"], "IDENTITY 端口缺失/不符"
        assert family_member["phone"] in family_member["identity"], "IDENTITY 热线缺失/不符"


class TestPersonaIntegrity:
    """人设完整性抽检：历史旧称禁入 + 家族精神在场 + SOUL 结构完整"""

    def test_no_legacy_name_in_prompts(self):
        # 生产提示词层严禁历史旧称「知遇·伯乐/知遇伯乐」（千里·伯乐 已归一）
        for dirname in FAMILY:
            for f in ("IDENTITY.md", "SOUL.md", "SYSTEM.md"):
                text = (AGENTS_DIR / dirname / f).read_text(encoding="utf-8")
                assert "知遇·伯乐" not in text and "知遇伯乐" not in text, f"{dirname}/{f} 含历史旧称"

    def test_soul_has_five_dimension_duties(self, family_member):
        assert "五维管理职能" in family_member["soul"], "SOUL.md 缺五维管理职能章节"

    def test_soul_has_behavior_constraints(self, family_member):
        assert "行为约束" in family_member["soul"], "SOUL.md 缺行为约束章节"

    def test_soul_has_family_oath(self, family_member):
        assert "家族誓言" in family_member["soul"], "SOUL.md 缺家族誓言章节"

    def test_system_has_collaboration_section(self, family_member):
        assert "协同" in family_member["system"], "SYSTEM.md 缺协同家族说明"

    def test_mbti_present(self, family_member):
        m = re.search(r"\| \*\*MBTI\*\* \| (\w{4}) \|", family_member["identity"])
        assert m, "IDENTITY.md 缺 MBTI"

    def test_hub_registry_covers_all_family(self):
        import sys
        sys.path.insert(0, str(REPO_ROOT))
        from governance_hub import AGENTS
        assert set(FAMILY[d][0] for d in FAMILY) == set(AGENTS)
