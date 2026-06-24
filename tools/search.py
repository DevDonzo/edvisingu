"""Tool 1 — Web search (Tavily). Mock by default (Manual 23.1)."""

import os

from tools import is_live


def web_search(query: str, max_results: int = 5) -> dict:
    if is_live("TAVILY_API_KEY"):  # pragma: no cover - needs key
        from tavily import TavilyClient

        client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
        result = client.search(query=query, max_results=max_results, search_depth="advanced")
        return {
            "query": query,
            "results": [
                {"title": r["title"], "url": r["url"], "content": r["content"]}
                for r in result["results"]
            ],
        }

    # Mock: deterministic, realistic-looking results.
    return {
        "query": query,
        "mock": True,
        "results": [
            {
                "title": f"Result {i + 1} for '{query}'",
                "url": f"https://example.com/{query.replace(' ', '-').lower()}-{i + 1}",
                "content": f"Mock summary {i + 1} about {query}. Set TAVILY_API_KEY + ARCH_BACKEND=live for real search.",
            }
            for i in range(min(max_results, 3))
        ],
    }
