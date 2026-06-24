"""ManyChat Messenger/Instagram DM tool (Manual 29.3). Mock by default ($0).

Funnel events route to hermes-funnel / hermes-crm via an n8n webhook
(``/webhook/manychat-lead``). Live mode needs ``MANYCHAT_API_KEY``.
"""

import os

from tools import is_live

MC_BASE = "https://api.manychat.com"


async def get_subscriber_info(subscriber_id: str) -> dict:
    if is_live("MANYCHAT_API_KEY"):  # pragma: no cover - needs key
        import httpx

        async with httpx.AsyncClient() as client:
            r = await client.get(
                f"{MC_BASE}/fb/subscriber/getInfo?subscriber_id={subscriber_id}",
                headers={"Authorization": f"Bearer {os.environ['MANYCHAT_API_KEY']}"},
            )
            return r.json()

    return {"mock": True, "subscriber_id": subscriber_id, "status": "active",
            "name": "Mock Subscriber", "tags": ["ig-dm", "ai-curious"],
            "source": "instagram"}


async def tag_subscriber(subscriber_id: str, tag_id: str) -> dict:
    if is_live("MANYCHAT_API_KEY"):  # pragma: no cover - needs key
        import httpx

        async with httpx.AsyncClient() as client:
            r = await client.post(
                f"{MC_BASE}/fb/subscriber/addTag",
                headers={"Authorization": f"Bearer {os.environ['MANYCHAT_API_KEY']}"},
                json={"subscriber_id": subscriber_id, "tag_id": tag_id},
            )
            return r.json()

    return {"mock": True, "status": "tagged", "subscriber_id": subscriber_id, "tag_id": tag_id}
