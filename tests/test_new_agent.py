"""Tests for the Section 31 agent creation framework generator."""

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("new_agent", ROOT / "scripts" / "new_agent.py")
new_agent = importlib.util.module_from_spec(_spec)
sys.modules["new_agent"] = new_agent
_spec.loader.exec_module(new_agent)


def test_normalize_name():
    assert new_agent.normalize_name("grants") == "hermes-grants"
    assert new_agent.normalize_name("hermes-grants") == "hermes-grants"
    assert new_agent.normalize_name("Grant Writer") == "hermes-grant-writer"


def test_create_agent_writes_four_files(tmp_path, monkeypatch):
    monkeypatch.setattr(new_agent, "_AGENTS_DIR", tmp_path)
    # The generator copies hermes-core/app.py as the template, so provide one.
    core = tmp_path / "hermes-core"
    core.mkdir()
    (core / "app.py").write_text('AGENT_NAME = "hermes-core"\n')

    result = new_agent.create_agent("grants", "Grant Writer", "haiku",
                                    ["Draft grant applications", "Track deadlines"])
    assert result["agent"] == "hermes-grants"
    assert result["model"] == "Claude Haiku 4.5"
    assert result["model_group"] == "HAIKU_AGENTS"

    agent_dir = tmp_path / "hermes-grants"
    for fname in ("SOUL.md", "app.py", "Dockerfile", "requirements.txt"):
        assert (agent_dir / fname).exists()

    soul = (agent_dir / "SOUL.md").read_text()
    assert "hermes-grants" in soul and "Grant Writer" in soul and "Claude Haiku 4.5" in soul
    # app.py was specialised from the template.
    assert 'AGENT_NAME = "hermes-grants"' in (agent_dir / "app.py").read_text()


def test_create_agent_no_overwrite_without_force(tmp_path, monkeypatch):
    monkeypatch.setattr(new_agent, "_AGENTS_DIR", tmp_path)
    core = tmp_path / "hermes-core"
    core.mkdir()
    (core / "app.py").write_text('AGENT_NAME = "hermes-core"\n')

    new_agent.create_agent("grants", "Grant Writer", "sonnet", [])
    second = new_agent.create_agent("grants", "Grant Writer", "sonnet", [])
    assert second["written"] == []  # nothing overwritten

    forced = new_agent.create_agent("grants", "Grant Writer", "sonnet", [], force=True)
    assert len(forced["written"]) == 4


def test_invalid_model_rejected(tmp_path, monkeypatch):
    monkeypatch.setattr(new_agent, "_AGENTS_DIR", tmp_path)
    with pytest.raises(ValueError):
        new_agent.create_agent("grants", "Grant Writer", "not-a-model", [])


def test_registration_instructions_include_port_and_group():
    text = new_agent.registration_instructions("hermes-grants", "HAIKU_AGENTS", 8028)
    assert '"hermes-grants": 8028' in text
    assert "HAIKU_AGENTS.add(\"hermes-grants\")" in text
    assert "docker compose build hermes-grants" in text
