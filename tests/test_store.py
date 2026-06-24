"""Tests for core.store — local SQLite layer ($0, no Supabase)."""

import importlib

import pytest


@pytest.fixture()
def store(tmp_path, monkeypatch):
    """Fresh, isolated DB per test."""
    monkeypatch.setenv("EDVISINGU_DB", str(tmp_path / "test.db"))
    import core.store as store_mod
    importlib.reload(store_mod)
    store_mod.init_db()
    return store_mod


def test_schema_creation(store):
    conn = store.connect()
    tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
    conn.close()
    assert {"leads", "members", "products", "content_queue", "ai_memory"} <= tables


def test_seed_populates(store):
    result = store.seed()
    assert result["seeded"] is True
    assert len(store.list_leads()) == 8
    assert len(store.list_members()) == 3
    assert len(store.list_products()) == 3


def test_seed_idempotent(store):
    store.seed()
    again = store.seed()
    assert again["seeded"] is False
    assert len(store.list_leads()) == 8


def test_insert_lead_roundtrip(store):
    store.insert_lead("Test User", "test@example.com", source="Discord", tags=["x", "y"])
    leads = [l for l in store.list_leads() if l["email"] == "test@example.com"]
    assert leads and leads[0]["tags"] == ["x", "y"]


def test_insert_content(store):
    store.insert_content("Test topic", "linkedin", final_content="body", status="published")
    published = store.list_content(status="published")
    assert any(c["topic"] == "Test topic" for c in published)


def test_whop_member_lifecycle(store):
    store.upsert_member("new@member.com", name="New Member", whop_id="w9", plan="premium")
    members = {m["email"]: m for m in store.list_members()}
    assert members["new@member.com"]["status"] == "active"
    store.deactivate_member("new@member.com")
    members = {m["email"]: m for m in store.list_members()}
    assert members["new@member.com"]["status"] == "cancelled"


def test_stats_rollup(store):
    store.seed()
    s = store.stats()
    assert s["leads_total"] == 8
    assert s["members"] == 3
    assert s["mrr"] == 3 * 47
    assert s["agents_online"] == 25
