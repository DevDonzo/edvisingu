"""MailerLite email platform tool (Manual 29.2). Mock by default ($0, no key).

hermes-email READS list data and DRAFTS content only. It must NOT send
campaigns automatically — all sends go through Lahari for QA and Dr. D's
explicit approval. Live mode needs ``MAILERLITE_API_KEY``.
"""

import os

from tools import is_live

ML_BASE = "https://connect.mailerlite.com/api"


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {os.environ['MAILERLITE_API_KEY']}",
        "Content-Type": "application/json",
    }


async def get_subscriber_count() -> dict:
    if is_live("MAILERLITE_API_KEY"):  # pragma: no cover - needs key
        import httpx

        async with httpx.AsyncClient() as client:
            r = await client.get(f"{ML_BASE}/subscribers?limit=1", headers=_headers())
            return {"total": r.json().get("meta", {}).get("total", 0)}

    return {"mock": True, "total": 3142}


async def get_campaigns() -> dict:
    if is_live("MAILERLITE_API_KEY"):  # pragma: no cover - needs key
        import httpx

        async with httpx.AsyncClient() as client:
            r = await client.get(f"{ML_BASE}/campaigns", headers=_headers())
            return {"campaigns": r.json().get("data", [])}

    campaigns = [
        {"id": "ml_1", "name": "EdVisingU — AI Side Hustle Blueprint", "status": "sent"},
        {"id": "ml_2", "name": "DrDDurham — Volunteer GOTV push", "status": "draft"},
    ]
    return {"mock": True, "campaigns": campaigns, "count": len(campaigns)}


async def add_subscriber(email: str, name: str = "") -> dict:
    if is_live("MAILERLITE_API_KEY"):  # pragma: no cover - needs key
        import httpx

        async with httpx.AsyncClient() as client:
            r = await client.post(
                f"{ML_BASE}/subscribers", headers=_headers(),
                json={"email": email, "fields": {"name": name}},
            )
            return r.json()

    return {"mock": True, "status": "added", "email": email, "name": name,
            "id": f"mock_sub_{abs(hash(email)) % 100000}"}
