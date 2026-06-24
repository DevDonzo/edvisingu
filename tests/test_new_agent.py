"""Tests for the Section 31 agent creation framework (souls + fleet structure)."""

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


def test_create_agent_writes_one_soul(tmp_path, monkeypatch):
    monkeypatch.setattr(new_agent, "_SOULS_DIR", tmp_path)
    result = new_agent.create_agent("grants", "Grant Writer", "haiku",
                                    ["Draft grant applications", "Track deadlines"])
    assert result["agent"] == "hermes-grants"
    assert result["model"] == "Claude Haiku 4.5"
    assert result["fleet_const"] == "HAIKU"
    assert result["written"] is True

    soul = (tmp_path / "hermes-grants.md").read_text()
    assert "hermes-grants" in soul and "Grant Writer" in soul and "Claude Haiku 4.5" in soul


def test_create_agent_no_overwrite_without_force(tmp_path, monkeypatch):
    monkeypatch.setattr(new_agent, "_SOULS_DIR", tmp_path)
    assert new_agent.create_agent("grants", "Grant Writer", "sonnet", [])["written"] is True
    assert new_agent.create_agent("grants", "Grant Writer", "sonnet", [])["written"] is False
    assert new_agent.create_agent("grants", "Grant Writer", "sonnet", [], force=True)["written"] is True


def test_invalid_model_rejected(tmp_path, monkeypatch):
    monkeypatch.setattr(new_agent, "_SOULS_DIR", tmp_path)
    with pytest.raises(ValueError):
        new_agent.create_agent("grants", "Grant Writer", "not-a-model", [])


def test_registration_line_is_a_fleet_entry():
    line = new_agent.registration_line("hermes-grants", "Grant Writer", "HAIKU", 8028)
    assert 'Agent("hermes-grants", 8028, HAIKU, "Grant Writer"' in line
