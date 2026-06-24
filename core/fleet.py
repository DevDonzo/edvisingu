"""The agent fleet — single source of truth.

Every other module (core.llm routing, demo_server, the router, run.py, the
generic agent app, docker-compose generation) derives the roster, ports, models,
roles and categories from this one list. Add an agent here and it shows up
everywhere; there is no second place to update.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent

# Canonical model ids (Manual Section 26). Display labels live in MODEL_LABELS.
SONNET = "claude-sonnet-4-6"
HAIKU = "claude-haiku-4-5"
GEMINI = "gemini-2.0-flash"
GPT4O = "gpt-4o"

MODEL_LABELS = {
    SONNET: "Claude Sonnet 4.6",
    HAIKU: "Claude Haiku 4.5",
    GEMINI: "Gemini 2.0 Flash",
    GPT4O: "GPT-4o",
}


@dataclass(frozen=True)
class Agent:
    name: str
    port: int
    model: str
    role: str
    category: str  # core | content | education | revenue | ops | dev

    @property
    def model_label(self) -> str:
        return MODEL_LABELS.get(self.model, self.model)


# The 25-agent fleet (Manual Sections 24 & 27). Ports 8007/8026 are intentionally
# skipped to match the historical container layout.
FLEET: list[Agent] = [
    Agent("hermes-core", 8001, SONNET, "Executive Assistant", "core"),
    Agent("hermes-content", 8002, SONNET, "Content Factory", "content"),
    Agent("hermes-advisor", 8003, SONNET, "Student Advisor", "education"),
    Agent("hermes-credihire", 8004, SONNET, "Resume & Career", "education"),
    Agent("hermes-ops", 8005, HAIKU, "System Monitor", "ops"),
    Agent("hermes-social", 8006, GEMINI, "Community Manager", "content"),
    Agent("hermes-builder", 8008, GPT4O, "Project Builder", "dev"),
    Agent("hermes-research", 8009, SONNET, "Intelligence", "core"),
    Agent("hermes-finance", 8010, HAIKU, "Revenue Tracker", "ops"),
    Agent("hermes-email", 8011, SONNET, "Communications", "core"),
    Agent("hermes-ads", 8012, GEMINI, "Ad Strategist", "content"),
    Agent("hermes-seo", 8013, GEMINI, "SEO Specialist", "content"),
    Agent("hermes-funnel", 8014, SONNET, "Funnel Architect", "revenue"),
    Agent("hermes-etsy", 8015, HAIKU, "Etsy Manager", "revenue"),
    Agent("hermes-outreach", 8016, SONNET, "Outbound Sales", "revenue"),
    Agent("hermes-proposals", 8017, SONNET, "Proposal Writer", "revenue"),
    Agent("hermes-crm", 8018, HAIKU, "CRM Assistant", "ops"),
    Agent("hermes-crediversity", 8019, SONNET, "LMS Builder", "education"),
    Agent("hermes-hireed", 8020, SONNET, "WIL Coordinator", "education"),
    Agent("hermes-educonnect", 8021, SONNET, "Platform Ops", "education"),
    Agent("hermes-whop", 8022, HAIKU, "Membership Ops", "revenue"),
    Agent("hermes-tiktok", 8023, GEMINI, "TikTok Creator", "content"),
    Agent("hermes-campaign", 8024, SONNET, "Campaign Manager", "content"),
    Agent("hermes-gumroad", 8025, HAIKU, "Product Sales", "revenue"),
    Agent("hermes-pinterest", 8027, GEMINI, "Pinterest SEO", "content"),
]

BY_NAME: dict[str, Agent] = {a.name: a for a in FLEET}

DEFAULT_MODEL = SONNET


def names() -> list[str]:
    return [a.name for a in FLEET]


def get(name: str) -> Agent | None:
    return BY_NAME.get(name)


def model_for(name: str | None) -> str:
    """Resolve which model an agent uses (Manual Section 26)."""
    agent = BY_NAME.get(name) if name else None
    return agent.model if agent else DEFAULT_MODEL


def ports() -> dict[str, int]:
    return {a.name: a.port for a in FLEET}


def routing() -> dict[str, list[str]]:
    """model id -> [agent names]."""
    out: dict[str, list[str]] = {}
    for a in FLEET:
        out.setdefault(a.model, []).append(a.name)
    return out


def soul_path(name: str) -> Path:
    """Personality file for an agent: souls/<name>.md."""
    return _ROOT / "souls" / f"{name}.md"
