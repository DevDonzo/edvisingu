"""Gemini API with web grounding (Manual 28.4). Mock by default ($0, no key).

Used by hermes-seo / hermes-ads / hermes-tiktok / hermes-social for live trend
and research queries. Live mode needs ``GOOGLE_AI_API_KEY`` (from aistudio).
"""

import os

from tools import is_live


def gemini_search(query: str) -> dict:
    if is_live("GOOGLE_AI_API_KEY"):  # pragma: no cover - needs key
        import google.generativeai as genai

        genai.configure(api_key=os.environ["GOOGLE_AI_API_KEY"])
        model = genai.GenerativeModel("gemini-2.0-flash")
        result = model.generate_content(query, tools=[{"google_search": {}}])
        return {"query": query, "text": result.text, "grounded": True}

    return {
        "mock": True,
        "query": query,
        "grounded": True,
        "text": (
            f"Web-grounded summary for '{query}': current signals point to rising interest among "
            "Canadian post-secondary students in AI side-income tools and OSAP optimization. "
            "Set GOOGLE_AI_API_KEY + ARCH_BACKEND=live for real Google Search grounding."
        ),
    }


def gemini_analyze(content: str, prompt: str) -> dict:
    if is_live("GOOGLE_AI_API_KEY"):  # pragma: no cover - needs key
        import google.generativeai as genai

        genai.configure(api_key=os.environ["GOOGLE_AI_API_KEY"])
        model = genai.GenerativeModel("gemini-2.0-flash")
        result = model.generate_content(f"{prompt}\n\nContent:\n{content}")
        return {"prompt": prompt, "text": result.text}

    return {
        "mock": True,
        "prompt": prompt,
        "text": (
            f"Analysis ({prompt}): the supplied content ({len(content)} chars) is on-brand and "
            "ready for review. Mock output — set GOOGLE_AI_API_KEY + ARCH_BACKEND=live for real analysis."
        ),
    }
