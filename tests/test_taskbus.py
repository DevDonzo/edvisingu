"""Tests for the file-based Agent Task Bus and orchestrator ($0, offline)."""

import importlib

import pytest


@pytest.fixture()
def bus(tmp_path, monkeypatch):
    monkeypatch.setenv("AGENT_BUS_DIR", str(tmp_path / "agent-bus"))
    monkeypatch.delenv("ARCH_BACKEND", raising=False)
    from tools import task_bus
    importlib.reload(task_bus)
    task_bus.clear()
    return task_bus


def test_publish_creates_inbox_task(bus):
    res = bus.publish_task("hermes-content", "generate", {"topic": "x"})
    assert res["queued"] is True
    inbox = list((bus.bus_dir() / "inbox").glob("*.json"))
    assert len(inbox) == 1


def test_full_lifecycle(bus):
    res = bus.publish_task("hermes-finance", "mrr", {"q": "this week"})
    tid = res["task_id"]
    task = bus.get_next_task("hermes-finance")
    assert task["task_id"] == tid and task["status"] == "working"
    # inbox emptied, working has the file
    assert not list((bus.bus_dir() / "inbox").glob("*.json"))
    assert list((bus.bus_dir() / "working").glob("*.json"))
    bus.complete_task(tid, {"answer": "MRR is $4,230"})
    out = bus.read_outbox(tid)
    assert out["status"] == "completed" and out["result"]["answer"] == "MRR is $4,230"
    # working emptied, outbox has the file
    assert not list((bus.bus_dir() / "working").glob("*.json"))


def test_get_next_task_filters_by_agent(bus):
    bus.publish_task("hermes-content", "a", {})
    assert bus.get_next_task("hermes-finance") is None
    assert bus.get_next_task("hermes-content") is not None


def test_orchestrator_dispatch(bus):
    from core import orchestrator
    result = orchestrator.dispatch("write a post", agent="hermes-content")
    assert result["status"] == "completed"
    assert result["stages"] == ["inbox", "working", "outbox"]
    assert result["result"]["answer"]
    assert result["model"] == "claude-sonnet-4-6"
