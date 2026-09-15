"""YYC³ Family-AI Agents 测试套件 — conftest"""
import os
import sys
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

# 必须在导入 governance_hub 之前设定：使用临时数据库
_TMP_DB = os.path.join(tempfile.gettempdir(), "yyc3-test-governance.db")
os.environ.setdefault("GOVERNANCE_DB", _TMP_DB)
os.environ.setdefault("GOVERNANCE_ENDPOINT", "http://localhost:25799")  # 不可达端口，测试静默旁路
os.environ.setdefault("VLLM_ENDPOINT", "http://localhost:29999/v1")
os.environ.setdefault("SYSTEM_PROMPT_PATH", str(REPO_ROOT / "agents" / "yuanqi-tianshu" / "SYSTEM.md"))


@pytest.fixture()
def gov_db(tmp_path, monkeypatch):
    """为 governance_hub 提供隔离的临时数据库"""
    import governance_hub
    db_path = str(tmp_path / "governance.db")
    monkeypatch.setattr(governance_hub, "DB_PATH", db_path)
    governance_hub.init_db()
    yield governance_hub
