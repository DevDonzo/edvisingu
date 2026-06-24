"""Tests that the OpenAI-compatible router and specialist agents all run
offline ($0, no API key) via core.llm.

(The standalone orchestration API in agents/main.py was removed during the
architecture consolidation — its endpoints live on in demo_server.py for the
demo and in router.py + the generic agent.py for the live VPS path.)
"""

import importlib.util
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(autouse=True)
def offline_env(tmp_path, monkeypatch):
    monkeypatch.delenv("ARCH_BACKEND", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setenv("EDVISINGU_DB", str(tmp_path / "router.db"))


def test_router_openai_compatible_offline():
    mod = _load(ROOT / "router.py", "router_main")
    client = TestClient(mod.app)

    assert client.get("/health").json()["backend"] == "mock"
    models = client.get("/v1/models").json()["data"]
    assert any(m["id"] == "hermes-builder" and m["model"] == "gpt-4o" for m in models)

    r = client.post("/v1/chat/completions", json={
        "model": "hermes-finance",
        "messages": [{"role": "user", "content": "revenue update"}],
    })
    data = r.json()
    assert data["choices"][0]["message"]["content"]
    assert data["model"] == "claude-haiku-4-5"


def test_specialist_agent_app_offline(monkeypatch):
    # One generic agent.py serves the whole fleet; AGENT_NAME selects identity.
    monkeypatch.setenv("AGENT_NAME", "hermes-finance")
    mod = _load(ROOT / "agent.py", "agent_app_finance")
    client = TestClient(mod.app)
    assert client.get("/health").json()["agent"] == "hermes-finance"
    assert client.get("/health").json()["model"] == "claude-haiku-4-5"
    r = client.post("/chat", json={"message": "mrr please"})
    assert r.status_code == 200 and len(r.json()["response"]) > 0
