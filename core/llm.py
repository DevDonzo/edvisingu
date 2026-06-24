"""Shared LLM client for the EdVisingU AI ecosystem.

Design goals
------------
* **$0 by default.** With no API keys and no configuration, every call returns
  a deterministic, useful mock response. Nothing in this module ever makes a
  paid network call unless ``ARCH_BACKEND=live`` *and* a matching API key is
  present.
* **Single interface.** Routers, agents, and the demo server all call
  :func:`chat`. The backend (mock vs live) is selected by environment.
* **Graceful fallback.** If ``ARCH_BACKEND=live`` but the required key is
  missing, we log a warning and fall back to the mock — we never crash and we
  never spend money the user did not ask to spend.

Environment
-----------
ARCH_BACKEND   "mock" (default) | "live"
ANTHROPIC_API_KEY / OPENAI_API_KEY / GOOGLE_AI_API_KEY   used only in live mode

Model routing (mirrors Master Build Manual Section 26)
------------------------------------------------------
claude-sonnet-4-6  -> default reasoning/writing
claude-haiku-4-5   -> fast/cheap ops tasks
gemini-2.0-flash   -> web-grounded / social tasks
gpt-4o             -> code generation (hermes-builder)
"""

from __future__ import annotations

import logging
import os
import random
from typing import Iterable

logger = logging.getLogger("edvisingu.llm")

# ---------------------------------------------------------------------------
# Configuration helpers
# ---------------------------------------------------------------------------

DEFAULT_MODEL = "claude-sonnet-4-6"

# Agent -> model assignment (Manual Section 26.1 / 26.3)
CODEX_AGENTS = {"hermes-builder"}
GEMINI_AGENTS = {"hermes-social", "hermes-seo", "hermes-tiktok", "hermes-ads", "hermes-pinterest"}
HAIKU_AGENTS = {"hermes-ops", "hermes-finance", "hermes-crm", "hermes-whop", "hermes-etsy", "hermes-gumroad"}


def backend() -> str:
    """Return the active backend: ``"mock"`` (default) or ``"live"``."""
    return os.environ.get("ARCH_BACKEND", "mock").strip().lower()


def model_for_agent(agent: str | None) -> str:
    """Resolve which model an agent would use (Manual Section 26)."""
    if not agent:
        return DEFAULT_MODEL
    if agent in CODEX_AGENTS:
        return "gpt-4o"
    if agent in GEMINI_AGENTS:
        return "gemini-2.0-flash"
    if agent in HAIKU_AGENTS:
        return "claude-haiku-4-5"
    return DEFAULT_MODEL


def _provider_for_model(model: str) -> str:
    if model.startswith("gpt"):
        return "openai"
    if model.startswith("gemini"):
        return "google"
    return "anthropic"


def _key_for_provider(provider: str) -> str:
    return {
        "anthropic": os.environ.get("ANTHROPIC_API_KEY", ""),
        "openai": os.environ.get("OPENAI_API_KEY", ""),
        "google": os.environ.get("GOOGLE_AI_API_KEY", "") or os.environ.get("GOOGLE_API_KEY", ""),
    }.get(provider, "")


# ---------------------------------------------------------------------------
# Mock backend (default, $0, deterministic-ish)
# ---------------------------------------------------------------------------

_REVENUE = """**Revenue Intelligence Report**

| Metric | This Week | Last Week | Delta |
|--------|-----------|-----------|-------|
| MRR | $4,230 | $3,995 | +5.9% |
| New Members | 8 | 5 | +60% |
| Churn | 1 | 2 | -50% |
| Gumroad Sales | $847 | $612 | +38.4% |

Top performer: the TikTok -> Whop funnel converted at 4.2% this week. At the current
growth rate the system projects $5,000 MRR by end of month. Recommend triggering a
re-engagement sequence for the 3 members approaching their 90-day mark."""

_CONTENT = """**Content Pipeline Status**

Published today:
- LinkedIn: "Why 90% of students leave $50K on the table" (1,247 impressions)
- TikTok: "OSAP hack nobody talks about" (12.4K views)

In queue (pending approval):
- Email newsletter: "The AI Side Hustle Blueprint"
- YouTube Short: "I built a 25-agent AI system for $30/month"

Generating now via hermes-tiktok + hermes-seo. Want me to approve the queue?"""

_DEFAULT = """Here's my strategic read on that:

The EdVisingU ecosystem sits at the intersection of AI automation and student income
generation — a market with no direct Canadian competitor. Immediate moves:
1. Push the Content Factory to generate 3 LinkedIn posts targeting OSAP-eligible students.
2. Route to hermes-finance for this week's MRR snapshot.
3. Dispatch a deep-research task to hermes-research on competitor positioning.

Each qualified lead from this cycle carries roughly $47/month LTV. Want me to dispatch
this to the content team or dig deeper on any point?"""

# Agent-specific opening lines give each specialist a distinct voice in mock mode.
_AGENT_FLAVOR = {
    "hermes-core": "Executive summary first, details after.",
    "hermes-content": "Content angle locked in.",
    "hermes-advisor": "Here's the student-first guidance:",
    "hermes-credihire": "Resume/career analysis:",
    "hermes-ops": "System health check:",
    "hermes-finance": "Numbers up front:",
    "hermes-research": "Research synthesis (sources cited):",
    "hermes-builder": "Build plan:",
    "hermes-social": "Community angle:",
    "hermes-email": "Draft (for your review, not sent):",
}


def _mock_reply(messages: list[dict], system: str | None, agent: str | None) -> str:
    """Deterministic keyword-routed mock reply — no network, no cost."""
    last = ""
    for m in reversed(messages):
        if m.get("role") == "user":
            last = str(m.get("content", ""))
            break
    text = last.lower()

    if any(w in text for w in ("revenue", "mrr", "money", "income", "sales", "churn")):
        body = _REVENUE
    elif any(w in text for w in ("content", "post", "write", "publish", "tiktok", "linkedin", "email")):
        body = _CONTENT
    else:
        body = _DEFAULT

    flavor = _AGENT_FLAVOR.get(agent or "", "")
    prefix = f"{flavor}\n\n" if flavor else ""
    return f"{prefix}{body}"


class MockLLM:
    """Zero-cost deterministic backend used everywhere by default."""

    def chat(self, messages: list[dict], system: str | None = None,
             model: str | None = None, agent: str | None = None) -> str:
        return _mock_reply(messages, system, agent)


# ---------------------------------------------------------------------------
# Live backend (opt-in only; never used without ARCH_BACKEND=live + a key)
# ---------------------------------------------------------------------------

class LiveLLM:
    """Real cloud providers. Selected only when ARCH_BACKEND=live.

    Falls back to the mock (with a warning) whenever the required key is
    absent, so enabling live mode partially never crashes the system.
    """

    def __init__(self) -> None:
        self._mock = MockLLM()

    def chat(self, messages: list[dict], system: str | None = None,
             model: str | None = None, agent: str | None = None) -> str:
        model = model or model_for_agent(agent)
        provider = _provider_for_model(model)
        key = _key_for_provider(provider)
        if not key:
            logger.warning(
                "ARCH_BACKEND=live but no %s key set; falling back to mock for model %s.",
                provider, model,
            )
            return self._mock.chat(messages, system, model, agent)
        try:
            if provider == "anthropic":
                return self._anthropic(messages, system, model)
            if provider == "openai":
                return self._openai(messages, system, model)
            if provider == "google":
                return self._google(messages, system, model)
        except Exception as exc:  # pragma: no cover - network/SDK errors
            logger.warning("Live call failed (%s); falling back to mock.", exc)
        return self._mock.chat(messages, system, model, agent)

    # -- provider implementations (imported lazily so they are never required) --
    def _anthropic(self, messages, system, model):  # pragma: no cover - needs key
        import anthropic

        client = anthropic.Anthropic(api_key=_key_for_provider("anthropic"))
        kwargs = {"model": model, "max_tokens": 4096, "messages": messages}
        if system:
            kwargs["system"] = system
        msg = client.messages.create(**kwargs)
        return "".join(getattr(b, "text", "") for b in msg.content)

    def _openai(self, messages, system, model):  # pragma: no cover - needs key
        import openai

        client = openai.OpenAI(api_key=_key_for_provider("openai"))
        msgs = ([{"role": "system", "content": system}] if system else []) + messages
        resp = client.chat.completions.create(model=model, messages=msgs)
        return resp.choices[0].message.content or ""

    def _google(self, messages, system, model):  # pragma: no cover - needs key
        import google.generativeai as genai

        genai.configure(api_key=_key_for_provider("google"))
        gm = genai.GenerativeModel(model, system_instruction=system)
        prompt = "\n".join(str(m.get("content", "")) for m in messages)
        return gm.generate_content(prompt).text


# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------

def get_backend():
    """Return the active backend instance based on ARCH_BACKEND."""
    if backend() == "live":
        return LiveLLM()
    return MockLLM()


def chat(messages: Iterable[dict], system: str | None = None,
         model: str | None = None, agent: str | None = None) -> str:
    """Send a chat request. Returns assistant text.

    Mock by default ($0, no key). Live only when ARCH_BACKEND=live and a key
    exists; otherwise transparently falls back to mock.
    """
    msgs = list(messages)
    return get_backend().chat(msgs, system=system, model=model, agent=agent)


def is_mock() -> bool:
    """True when running without live cloud calls (the default)."""
    return not isinstance(get_backend(), LiveLLM) or backend() != "live"
