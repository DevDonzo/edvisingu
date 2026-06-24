"""Tests for Section 28 (Google Workspace) and Section 29 (platform) tools.

All offline / mock ($0, no keys). Async tools are driven via asyncio.run so we
don't need a pytest-asyncio plugin.
"""

import asyncio

import pytest

from tools import (
    is_live,
    gmail_tools,
    calendar_tools,
    gemini_tools,
    drive_tools,
    blotato_tools,
    mailerlite_tools,
    manychat_tools,
    disco_tools,
)


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    monkeypatch.delenv("ARCH_BACKEND", raising=False)
    for k in ("GOOGLE_REFRESH_TOKEN", "GOOGLE_AI_API_KEY", "BLOTATO_API_KEY",
              "MAILERLITE_API_KEY", "MANYCHAT_API_KEY", "DISCO_API_KEY"):
        monkeypatch.delenv(k, raising=False)


# ── Section 28: Google Workspace ──────────────────────

def test_gmail_recent_and_send_mock():
    recent = gmail_tools.get_recent_emails(max_results=2)
    assert recent["mock"] is True and recent["count"] == 2
    sent = gmail_tools.send_email("x@y.ca", "Hi", "Body")
    assert sent["mock"] is True and sent["status"] == "sent" and sent["to"] == "x@y.ca"


def test_calendar_mock():
    today = calendar_tools.get_todays_events()
    assert today["mock"] is True and today["count"] >= 1
    evt = calendar_tools.create_event("Meet", "2026-06-23T09:00:00", "2026-06-23T09:30:00")
    assert evt["mock"] is True and evt["timezone"] == "America/Toronto"


def test_gemini_mock():
    out = gemini_tools.gemini_search("canadian student ai tools")
    assert out["mock"] is True and out["grounded"] is True and "query" in out
    analyzed = gemini_tools.gemini_analyze("some content", "summarize")
    assert analyzed["mock"] is True and "text" in analyzed


def test_drive_mock():
    recent = drive_tools.list_recent_files(max_results=3)
    assert recent["mock"] is True and recent["count"] == 3
    found = drive_tools.search_files("campaign")
    assert found["mock"] is True and found["query"] == "campaign"


# ── Section 29: Platform integrations part 2 ──────────

def test_blotato_mock():
    out = asyncio.run(blotato_tools.schedule_post("post", ["facebook", "tiktok"], "2026-06-23T12:00:00"))
    assert out["mock"] is True and out["status"] == "scheduled" and "facebook" in out["platforms"]
    recent = asyncio.run(blotato_tools.get_recent_posts(2))
    assert recent["mock"] is True and recent["count"] == 2


def test_mailerlite_mock():
    count = asyncio.run(mailerlite_tools.get_subscriber_count())
    assert count["mock"] is True and isinstance(count["total"], int)
    camps = asyncio.run(mailerlite_tools.get_campaigns())
    assert camps["mock"] is True and camps["count"] >= 1
    sub = asyncio.run(mailerlite_tools.add_subscriber("a@b.ca", "A"))
    assert sub["mock"] is True and sub["status"] == "added"


def test_manychat_mock():
    info = asyncio.run(manychat_tools.get_subscriber_info("sub_1"))
    assert info["mock"] is True and info["subscriber_id"] == "sub_1"
    tagged = asyncio.run(manychat_tools.tag_subscriber("sub_1", "tag_9"))
    assert tagged["mock"] is True and tagged["status"] == "tagged"


def test_disco_mock():
    courses = asyncio.run(disco_tools.get_courses())
    assert courses["mock"] is True and courses["count"] >= 1
    enr = asyncio.run(disco_tools.get_enrollments("crs_ai101"))
    assert enr["mock"] is True and enr["course_id"] == "crs_ai101"
    enrolled = asyncio.run(disco_tools.enroll_learner("crs_ai101", "a@b.ca"))
    assert enrolled["mock"] is True and enrolled["status"] == "enrolled"


def test_all_tools_default_to_mock():
    """No key + no live flag → every new tool stays mock ($0)."""
    assert is_live("GOOGLE_REFRESH_TOKEN") is False
    assert is_live("BLOTATO_API_KEY") is False
