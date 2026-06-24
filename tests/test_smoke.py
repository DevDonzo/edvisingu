"""Section 15 (Manual) integration smoke test — the whole system, offline ($0).

Mirrors the manual's "Full System Integration Test" checklist, adapted to the
local mock-first stack: store, demo API surface, agent fleet, and task bus all
work end-to-end with no API key.
"""

import importlib
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture()
def env(tmp_path, monkeypatch):
    monkeypatch.delenv("ARCH_BACKEND", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setenv("EDVISINGU_DB", str(tmp_path / "smoke.db"))
    monkeypatch.setenv("AGENT_BUS_DIR", str(tmp_path / "bus"))


def test_section15_full_system(env):
    # Store layer (replaces Supabase)
    import core.store as store
    importlib.reload(store)
    store.ensure_seeded()
    assert store.stats()["agents_online"] == 25

    # Demo API surface (dashboard backend)
    import demo_server
    importlib.reload(demo_server)
    client = TestClient(demo_server.app)

    assert client.get("/health").json()["status"] == "operational"          # health
    assert client.post("/chat", json={"message": "hi"}).json()["response"]   # chat
    assert "linkedin" in client.post("/content/generate",
                                     json={"topic": "AI", "platforms": ["linkedin"]}).json()["content"]
    assert client.post("/hermes/chat", json={"message": "revenue"}).json()["response"]
    assert client.post("/advisor/chat", json={"message": "help"}).json()["agent"] == "hermes-advisor"
    assert "ats_score" in client.post("/credihire/analyze", json={"resume_text": "x"}).json()
    assert client.get("/agents").json()["total"] == 25
    assert client.get("/monitoring").json()["down"] == 0
    assert client.get("/routing").json()["total_agents"] >= 25

    # Whop webhook -> store
    client.post("/whop/webhook", json={"event": "member.created", "email": "s@test.com", "name": "S"})
    assert any(m["email"] == "s@test.com" for m in client.get("/members").json()["members"])


def test_section15_orchestrator_offline(env):
    import tools.task_bus as tb
    importlib.reload(tb)
    from core import orchestrator
    importlib.reload(orchestrator)
    result = orchestrator.dispatch("write a hook", agent="hermes-content")
    assert result["status"] == "completed" and result["result"]["answer"]
