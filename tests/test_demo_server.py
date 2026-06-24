"""Tests for demo_server.py — the dashboard's mock API ($0, no keys)."""

import importlib
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("EDVISINGU_DB", str(tmp_path / "demo.db"))
    monkeypatch.delenv("ARCH_BACKEND", raising=False)
    import demo_server
    importlib.reload(demo_server)
    return TestClient(demo_server.app)


def test_existing_contract_stable(client):
    assert client.get("/health").json()["status"] == "operational"
    assert client.get("/agents").json()["total"] == 25
    leads = client.get("/leads").json()
    assert "leads" in leads and leads["total"] >= 1


def test_credihire_optimize_cover_linkedin(client):
    assert "optimized_resume" in client.post("/credihire/optimize", json={"resume_text": "x"}).json()
    assert "cover_letter" in client.post("/credihire/cover-letter", json={"resume_text": "x"}).json()
    assert "linkedin_summary" in client.post("/credihire/linkedin-summary", json={"resume_text": "x"}).json()


def test_heygen_and_elevenlabs_mock(client):
    hg = client.post("/heygen/generate", json={"script": "hello"}).json()
    assert hg["mock"] is True and "video_id" in hg
    el = client.post("/elevenlabs/speak", json={"text": "hello world"}).json()
    assert el["mock"] is True and el["audio_path"].endswith(".mp3")


def test_whop_webhook_updates_store(client):
    r = client.post("/whop/webhook", json={"event": "member.created", "email": "w@test.com", "name": "W"})
    assert r.json()["result"]["status"] == "active"
    members = client.get("/members").json()
    assert any(m["email"] == "w@test.com" for m in members["members"])
    r2 = client.post("/whop/webhook", json={"event": "member.deleted", "email": "w@test.com"})
    assert r2.json()["result"]["status"] == "cancelled"


def test_content_persists(client):
    client.post("/content/generate", json={"topic": "Test topic", "platforms": ["linkedin"]})
    content = client.get("/content").json()
    assert any(c["topic"] == "Test topic" for c in content["content"])


def test_taskbus_demo(client):
    r = client.post("/taskbus/demo", json={"message": "do a thing", "agent": "hermes-content"}).json()
    assert r["status"] == "completed"
    stages = [s["stage"] for s in r["flow"]]
    assert stages == ["inbox", "working", "outbox"]


def test_routing_summary(client):
    r = client.get("/routing").json()
    assert r["models"]["gpt-4o"]["agents"] == ["hermes-builder"]
    assert r["total_agents"] >= 25


def test_monitoring_rollup(client):
    r = client.get("/monitoring").json()
    assert r["up"] == r["total"]
    assert r["down"] == 0


def test_campaign_brand_and_compliance(client):
    r = client.get("/campaign/brand").json()
    assert r["brand"]["name"] == "DrDDurham"
    assert r["brand"]["election_date"] == "2026-10-26"
    assert len(r["compliance"]) == 5
    assert "Authorized by" in r["authorization_line"]


def test_campaign_generate_weekly_batch(client):
    r = client.post("/campaign/generate", json={"theme": "Ward 2 doorknock recap"}).json()
    # Manual 30.3: 7 Facebook, 5 TikTok, 3 Instagram, 2 email.
    assert r["counts"] == {"facebook": 7, "tiktok": 5, "instagram": 3, "email": 2}
    assert r["status"] == "pending_approval"
    # Every published-channel item carries the legal authorization line (Manual 30.4).
    for post in r["content"]["facebook_posts"]:
        assert "Authorized by" in post["post"]
    # Drafts persisted to the local store for review.
    assert len(r["saved_content_ids"]) == 15


def test_campaign_schedule_uses_blotato_mock(client):
    r = client.post("/campaign/schedule", json={"post_ids": ["p1", "p2"]}).json()
    assert r["scheduled"]["mock"] is True
    assert r["scheduled"]["status"] == "scheduled"
    assert "Authorized by" in r["authorization_line"]
