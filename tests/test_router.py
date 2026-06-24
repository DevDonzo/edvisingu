"""Tests that the orchestration API, router, and specialist agents all run
offline ($0, no API key) via core.llm."""

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


def test_orchestration_api_endpoints():
    mod = _load(ROOT / "agents" / "main.py", "agents_main")
    client = TestClient(mod.app)

    assert client.get("/health").json()["ecosystem"] == "EdVisingU"

    r = client.post("/chat", json={"message": "what's our mrr?", "agent": "hermes-finance"})
    assert r.status_code == 200 and len(r.json()["response"]) > 0

    r = client.post("/content/generate", json={"topic": "AI for students", "platforms": ["linkedin"]})
    assert r.status_code == 200 and "linkedin" in r.json()["content"]

    r = client.post("/advisor/chat", json={"message": "how do I earn while studying?"})
    assert r.json()["agent"] == "student-advisor"

    r = client.post("/credihire/analyze", json={"resume_text": "Sample resume"})
    assert "analysis" in r.json()

    r = client.post("/credihire/optimize", json={"resume_text": "Sample", "job_description": "Dev"})
    assert "optimized_resume" in r.json()

    r = client.post("/credihire/cover-letter", json={"resume_text": "Sample", "job_description": "Dev"})
    assert "cover_letter" in r.json()


def test_heygen_and_elevenlabs_mock():
    mod = _load(ROOT / "agents" / "main.py", "agents_main2")
    client = TestClient(mod.app)
    hg = client.post("/heygen/generate", json={"script": "Hello world"}).json()
    assert hg["mock"] is True and "video_id" in hg
    el = client.post("/elevenlabs/speak", json={"text": "Hello"}).json()
    assert el["mock"] is True and el["audio_path"].endswith(".mp3")


def test_agent_fleet_route_offline():
    mod = _load(ROOT / "agents" / "main.py", "agents_main3")
    client = TestClient(mod.app)
    r = client.post("/agent/hermes-content/chat", json={"message": "write a post"})
    body = r.json()
    assert r.status_code == 200
    assert body["agent"] == "hermes-content"
    assert body["model"] == "claude-sonnet-4-6"


def test_router_openai_compatible_offline():
    mod = _load(ROOT / "fastapi-router" / "main.py", "fastapi_router_main")
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


def test_specialist_agent_app_offline():
    mod = _load(ROOT / "vps-agents" / "agents" / "hermes-finance" / "app.py", "hermes_finance_app")
    client = TestClient(mod.app)
    assert client.get("/health").json()["agent"] == "hermes-finance"
    r = client.post("/chat", json={"message": "mrr please"})
    assert r.status_code == 200 and len(r.json()["response"]) > 0
