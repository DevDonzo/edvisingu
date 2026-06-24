"""Blotato social scheduling tool (Manual 29.1). Mock by default ($0, no key).

Multi-platform publish (Facebook, Instagram, TikTok, X, LinkedIn, YouTube) in
one call. Used by hermes-content / hermes-social / hermes-tiktok /
hermes-campaign. Live mode needs ``BLOTATO_API_KEY``.
"""

import os

from tools import is_live

BLOTATO_BASE = "https://api.blotato.com/v1"


async def schedule_post(content: str, platforms: list, scheduled_at: str) -> dict:
    if is_live("BLOTATO_API_KEY"):  # pragma: no cover - needs key
        import httpx

        async with httpx.AsyncClient() as client:
            r = await client.post(
                f"{BLOTATO_BASE}/posts",
                headers={"Authorization": f"Bearer {os.environ['BLOTATO_API_KEY']}"},
                json={"content": content, "platforms": platforms, "scheduled_at": scheduled_at},
            )
            return r.json()

    return {"mock": True, "status": "scheduled",
            "post_id": f"mock_post_{abs(hash(content)) % 100000}",
            "platforms": platforms, "scheduled_at": scheduled_at,
            "note": "Mock Blotato schedule. Set BLOTATO_API_KEY + ARCH_BACKEND=live to publish."}


async def get_recent_posts(limit: int = 10) -> dict:
    if is_live("BLOTATO_API_KEY"):  # pragma: no cover - needs key
        import httpx

        async with httpx.AsyncClient() as client:
            r = await client.get(
                f"{BLOTATO_BASE}/posts?limit={limit}",
                headers={"Authorization": f"Bearer {os.environ['BLOTATO_API_KEY']}"},
            )
            return r.json()

    posts = [
        {"id": f"mock_post_{i}", "platforms": ["facebook", "instagram", "tiktok"],
         "status": "published", "content": f"DrDDurham update #{i + 1}"}
        for i in range(min(limit, 3))
    ]
    return {"mock": True, "posts": posts, "count": len(posts)}
