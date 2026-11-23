"""W1-B pip 包骨架契约测试 — pyproject 元数据 + cli 三入口行为（docs/13- 路径 C）"""
import json
import sqlite3
import tomllib
from pathlib import Path

import cli

REPO = Path(__file__).resolve().parent.parent.parent


def _load_pyproject():
    return tomllib.load(open(REPO / "pyproject.toml", "rb"))


def test_pyproject_metadata_complete():
    d = _load_pyproject()
    p = d["project"]
    assert p["name"] == "yyc3-family-ai"
    assert p["version"] == "3.1.0"
    assert p["requires-python"] == ">=3.10"
    assert p["dependencies"] == []
    assert set(d["tool"]["setuptools"]["py-modules"]) == {
        "guardrails", "semantic_layer", "memory_semantic", "durable", "cli"}


def test_entry_points_map_to_cli_functions():
    scripts = _load_pyproject()["project"]["scripts"]
    assert set(scripts) == {"yyc3-chat", "yyc3-audit", "yyc3-mdl"}
    assert scripts["yyc3-chat"] == "cli:chat"
    assert scripts["yyc3-audit"] == "cli:audit"
    assert scripts["yyc3-mdl"] == "cli:mdl_validate"


def test_cli_mdl_validates_demo_model(capsys):
    assert cli.main(["mdl", "--file", str(REPO / "mdl" / "demo.mdl.yaml")]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["status"] == "ok"
    assert "users" in out["tables"] and "total_users" in out["metrics"]


def test_cli_audit_reads_governance_db(tmp_path, capsys):
    db = tmp_path / "governance.db"
    conn = sqlite3.connect(str(db))
    conn.execute("CREATE TABLE behavior_events (id INTEGER PRIMARY KEY, agent TEXT, action TEXT, details TEXT, correlation_id TEXT, timestamp TEXT)")
    conn.execute("INSERT INTO behavior_events (agent, action, details, correlation_id, timestamp) VALUES ('tianshu', 'mcp_tool_call', '{}', 'c1', '2026-11-24T00:00:00')")
    conn.commit()
    conn.close()
    assert cli.main(["audit", "--db", str(db), "--limit", "10"]) == 0
    events = json.loads(capsys.readouterr().out)
    assert events[0]["agent"] == "tianshu"


def test_cli_audit_missing_db_fails_cleanly(tmp_path):
    assert cli.main(["audit", "--db", str(tmp_path / "missing.db")]) == 2