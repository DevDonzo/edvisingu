"""Local SQLite data layer — the $0 stand-in for Supabase.

The Master Build Manual (Section 8) uses a hosted Supabase/Postgres project.
That costs money and needs an account, so for local development we mirror the
same table shapes in a single SQLite file. The public helpers here are what the
demo server and dashboard consume, so swapping to real Supabase later only means
changing this module.

DB location: ``data/edvisingu.db`` (override with ``EDVISINGU_DB``).
Tables mirror ``api-configs/schema.sql``: leads, content_queue, products,
members, ai_memory (pgvector-specific bits dropped; tags/metadata stored as JSON).
"""

from __future__ import annotations

import json
import os
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_DEFAULT_DB = _PROJECT_ROOT / "data" / "edvisingu.db"


def _db_path() -> Path:
    return Path(os.environ.get("EDVISINGU_DB", str(_DEFAULT_DB)))


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_id() -> str:
    return str(uuid.uuid4())


def connect() -> sqlite3.Connection:
    path = _db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    return conn


SCHEMA = """
CREATE TABLE IF NOT EXISTS ai_memory (
    id TEXT PRIMARY KEY,
    agent_name TEXT NOT NULL,
    content TEXT NOT NULL,
    metadata TEXT,
    created_at TEXT
);
CREATE TABLE IF NOT EXISTS leads (
    id TEXT PRIMARY KEY,
    name TEXT,
    email TEXT UNIQUE,
    source TEXT,
    status TEXT DEFAULT 'new',
    tags TEXT,
    notes TEXT,
    created_at TEXT
);
CREATE TABLE IF NOT EXISTS content_queue (
    id TEXT PRIMARY KEY,
    topic TEXT NOT NULL,
    platform TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    raw_content TEXT,
    final_content TEXT,
    scheduled_at TEXT,
    published_at TEXT,
    created_at TEXT
);
CREATE TABLE IF NOT EXISTS products (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    price REAL,
    description TEXT,
    platform TEXT,
    url TEXT,
    active INTEGER DEFAULT 1,
    created_at TEXT
);
CREATE TABLE IF NOT EXISTS members (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    name TEXT,
    whop_id TEXT,
    plan TEXT,
    status TEXT DEFAULT 'active',
    joined_at TEXT
);
"""


def init_db(conn: sqlite3.Connection | None = None) -> None:
    """Create all tables if they do not exist."""
    own = conn is None
    conn = conn or connect()
    try:
        conn.executescript(SCHEMA)
        conn.commit()
    finally:
        if own:
            conn.close()


# ---------------------------------------------------------------------------
# Seed data (mirrors the mock data shipped in demo_server.py)
# ---------------------------------------------------------------------------

_SEED_LEADS = [
    {"name": "Sarah Chen", "email": "sarah.c@uoft.ca", "source": "TikTok", "status": "warm", "tags": ["OSAP", "AI-curious"]},
    {"name": "Marcus Williams", "email": "m.williams@ryerson.ca", "source": "LinkedIn", "status": "hot", "tags": ["coaching", "career-change"]},
    {"name": "Priya Patel", "email": "priya.p@mcmaster.ca", "source": "Whop", "status": "member", "tags": ["premium", "content-creator"]},
    {"name": "James Okafor", "email": "j.okafor@yorku.ca", "source": "Discord", "status": "new", "tags": ["BSWD", "first-gen"]},
    {"name": "Emily Tran", "email": "etran@uwaterloo.ca", "source": "Referral", "status": "warm", "tags": ["dev", "WIL-interest"]},
    {"name": "David Kim", "email": "d.kim@ubc.ca", "source": "Instagram", "status": "new", "tags": ["AI-tools", "side-hustle"]},
    {"name": "Aisha Mohammed", "email": "aisha.m@uottawa.ca", "source": "TikTok", "status": "hot", "tags": ["micro-cred", "resume-help"]},
    {"name": "Liam O'Brien", "email": "liam.ob@dal.ca", "source": "Email Campaign", "status": "warm", "tags": ["freelance", "AI-services"]},
]

_SEED_MEMBERS = [
    {"email": "priya.p@mcmaster.ca", "name": "Priya Patel", "whop_id": "whop_001", "plan": "premium", "status": "active"},
    {"email": "alex.r@queensu.ca", "name": "Alex Rivera", "whop_id": "whop_002", "plan": "standard", "status": "active"},
    {"email": "nadia.h@carleton.ca", "name": "Nadia Hassan", "whop_id": "whop_003", "plan": "premium", "status": "active"},
]

_SEED_PRODUCTS = [
    {"name": "EdVisingU Membership", "type": "membership", "price": 47.0, "platform": "Whop", "url": "https://whop.com/edvisingu", "description": "Monthly AI + income community"},
    {"name": "CrediHire Resume Engine", "type": "tool", "price": 47.0, "platform": "Skillplate", "url": "https://skillplate.com/credihire", "description": "ATS scoring + optimization"},
    {"name": "AI Side Hustle Blueprint", "type": "course", "price": 97.0, "platform": "Gumroad", "url": "https://gumroad.com/edvisingu", "description": "Build an AI income stream"},
]

_SEED_CONTENT = [
    {"topic": "How Canadian students can earn $500/month using AI tools", "platform": "linkedin", "status": "published", "final_content": "Sample published LinkedIn post."},
    {"topic": "OSAP hack nobody talks about", "platform": "tiktok", "status": "published", "final_content": "Sample published TikTok script."},
    {"topic": "The AI Side Hustle Blueprint", "platform": "email", "status": "pending", "raw_content": "Draft newsletter."},
]


def seed(conn: sqlite3.Connection | None = None, force: bool = False) -> dict:
    """Populate tables with demo data. No-op if leads already exist (unless force)."""
    own = conn is None
    conn = conn or connect()
    try:
        init_db(conn)
        existing = conn.execute("SELECT COUNT(*) AS c FROM leads").fetchone()["c"]
        if existing and not force:
            return {"seeded": False, "reason": "already populated"}
        if force:
            for t in ("leads", "members", "products", "content_queue", "ai_memory"):
                conn.execute(f"DELETE FROM {t}")
        for lead in _SEED_LEADS:
            conn.execute(
                "INSERT OR IGNORE INTO leads (id,name,email,source,status,tags,created_at) VALUES (?,?,?,?,?,?,?)",
                (_new_id(), lead["name"], lead["email"], lead["source"], lead["status"], json.dumps(lead["tags"]), _now()),
            )
        for m in _SEED_MEMBERS:
            conn.execute(
                "INSERT OR IGNORE INTO members (id,email,name,whop_id,plan,status,joined_at) VALUES (?,?,?,?,?,?,?)",
                (_new_id(), m["email"], m["name"], m["whop_id"], m["plan"], m["status"], _now()),
            )
        for p in _SEED_PRODUCTS:
            conn.execute(
                "INSERT INTO products (id,name,type,price,description,platform,url,active,created_at) VALUES (?,?,?,?,?,?,?,?,?)",
                (_new_id(), p["name"], p["type"], p["price"], p["description"], p["platform"], p["url"], 1, _now()),
            )
        for c in _SEED_CONTENT:
            conn.execute(
                "INSERT INTO content_queue (id,topic,platform,status,raw_content,final_content,created_at) VALUES (?,?,?,?,?,?,?)",
                (_new_id(), c["topic"], c["platform"], c.get("status", "pending"), c.get("raw_content"), c.get("final_content"), _now()),
            )
        conn.commit()
        return {"seeded": True}
    finally:
        if own:
            conn.close()


def ensure_seeded() -> None:
    """Initialise + seed the default DB if empty. Safe to call on import/startup."""
    seed()


# ---------------------------------------------------------------------------
# Read helpers
# ---------------------------------------------------------------------------

def _row_to_dict(row: sqlite3.Row) -> dict:
    d = dict(row)
    if "tags" in d and d["tags"]:
        try:
            d["tags"] = json.loads(d["tags"])
        except (TypeError, json.JSONDecodeError):
            d["tags"] = []
    elif "tags" in d:
        d["tags"] = []
    return d


def list_leads() -> list[dict]:
    conn = connect()
    try:
        rows = conn.execute("SELECT * FROM leads ORDER BY created_at DESC").fetchall()
        return [_row_to_dict(r) for r in rows]
    finally:
        conn.close()


def list_members() -> list[dict]:
    conn = connect()
    try:
        rows = conn.execute("SELECT * FROM members ORDER BY joined_at DESC").fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def list_products() -> list[dict]:
    conn = connect()
    try:
        rows = conn.execute("SELECT * FROM products ORDER BY created_at DESC").fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def list_content(status: str | None = None) -> list[dict]:
    conn = connect()
    try:
        if status:
            rows = conn.execute(
                "SELECT * FROM content_queue WHERE status=? ORDER BY created_at DESC", (status,)
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM content_queue ORDER BY created_at DESC").fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Write helpers
# ---------------------------------------------------------------------------

def insert_lead(name: str, email: str, source: str = "manual",
                status: str = "new", tags: list[str] | None = None, notes: str = "") -> dict:
    conn = connect()
    try:
        init_db(conn)
        lead_id = _new_id()
        conn.execute(
            "INSERT OR IGNORE INTO leads (id,name,email,source,status,tags,notes,created_at) VALUES (?,?,?,?,?,?,?,?)",
            (lead_id, name, email, source, status, json.dumps(tags or []), notes, _now()),
        )
        conn.commit()
        return {"id": lead_id, "email": email}
    finally:
        conn.close()


def insert_content(topic: str, platform: str, raw_content: str = "",
                   final_content: str = "", status: str = "pending") -> dict:
    conn = connect()
    try:
        init_db(conn)
        cid = _new_id()
        conn.execute(
            "INSERT INTO content_queue (id,topic,platform,status,raw_content,final_content,created_at) VALUES (?,?,?,?,?,?,?)",
            (cid, topic, platform, status, raw_content, final_content, _now()),
        )
        conn.commit()
        return {"id": cid, "topic": topic, "platform": platform, "status": status}
    finally:
        conn.close()


def upsert_member(email: str, name: str = "", whop_id: str = "",
                  plan: str = "standard", status: str = "active") -> dict:
    """Insert or reactivate a member (used by the Whop member.created webhook)."""
    conn = connect()
    try:
        init_db(conn)
        existing = conn.execute("SELECT id FROM members WHERE email=?", (email,)).fetchone()
        if existing:
            conn.execute(
                "UPDATE members SET name=?, whop_id=?, plan=?, status=? WHERE email=?",
                (name, whop_id, plan, status, email),
            )
            mid = existing["id"]
        else:
            mid = _new_id()
            conn.execute(
                "INSERT INTO members (id,email,name,whop_id,plan,status,joined_at) VALUES (?,?,?,?,?,?,?)",
                (mid, email, name, whop_id, plan, status, _now()),
            )
        conn.commit()
        return {"id": mid, "email": email, "status": status}
    finally:
        conn.close()


def deactivate_member(email: str) -> dict:
    """Mark a member cancelled (used by the Whop member.deleted webhook)."""
    conn = connect()
    try:
        init_db(conn)
        conn.execute("UPDATE members SET status='cancelled' WHERE email=?", (email,))
        conn.commit()
        return {"email": email, "status": "cancelled"}
    finally:
        conn.close()


def add_memory(agent_name: str, content: str, metadata: dict | None = None) -> dict:
    conn = connect()
    try:
        init_db(conn)
        mid = _new_id()
        conn.execute(
            "INSERT INTO ai_memory (id,agent_name,content,metadata,created_at) VALUES (?,?,?,?,?)",
            (mid, agent_name, content, json.dumps(metadata or {}), _now()),
        )
        conn.commit()
        return {"id": mid}
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Aggregates for the dashboard /stats endpoint
# ---------------------------------------------------------------------------

def stats() -> dict:
    conn = connect()
    try:
        leads = conn.execute("SELECT COUNT(*) AS c FROM leads").fetchone()["c"]
        members = conn.execute("SELECT COUNT(*) AS c FROM members WHERE status='active'").fetchone()["c"]
        content_total = conn.execute("SELECT COUNT(*) AS c FROM content_queue").fetchone()["c"]
        content_pending = conn.execute("SELECT COUNT(*) AS c FROM content_queue WHERE status='pending'").fetchone()["c"]
        content_published = conn.execute("SELECT COUNT(*) AS c FROM content_queue WHERE status='published'").fetchone()["c"]
        return {
            "mrr": members * 47,
            "members": members,
            "leads_total": leads,
            "content_total": content_total,
            "content_in_queue": content_pending,
            "content_published": content_published,
            "agents_online": 25,
            "uptime_percent": 99.7,
        }
    finally:
        conn.close()


if __name__ == "__main__":
    ensure_seeded()
    print("DB ready at", _db_path())
    print("stats:", stats())
