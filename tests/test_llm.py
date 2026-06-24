"""Tests for core.llm — offline-first behaviour ($0, no keys)."""

import importlib
import os

import pytest

import core.llm as llm


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    """Default every test to mock mode with no keys."""
    for var in ("ARCH_BACKEND", "ANTHROPIC_API_KEY", "OPENAI_API_KEY",
                "GOOGLE_AI_API_KEY", "GOOGLE_API_KEY"):
        monkeypatch.delenv(var, raising=False)
    yield


def test_default_backend_is_mock():
    assert llm.backend() == "mock"
    assert isinstance(llm.get_backend(), llm.MockLLM)


def test_chat_no_key_returns_text():
    out = llm.chat([{"role": "user", "content": "hello there"}])
    assert isinstance(out, str) and len(out) > 0


def test_revenue_keyword_routing():
    out = llm.chat([{"role": "user", "content": "what's our MRR this week?"}])
    assert "Revenue" in out or "MRR" in out


def test_content_keyword_routing():
    out = llm.chat([{"role": "user", "content": "write a tiktok post"}])
    assert "Content" in out


def test_agent_flavor_prefix():
    out = llm.chat([{"role": "user", "content": "status"}], agent="hermes-finance")
    assert out.startswith("Numbers up front")


def test_model_routing_matrix():
    assert llm.model_for_agent("hermes-builder") == "gpt-4o"
    assert llm.model_for_agent("hermes-seo") == "gemini-2.0-flash"
    assert llm.model_for_agent("hermes-finance") == "claude-haiku-4-5"
    assert llm.model_for_agent("hermes-core") == "claude-sonnet-4-6"
    assert llm.model_for_agent(None) == "claude-sonnet-4-6"


def test_live_without_key_falls_back_to_mock(monkeypatch):
    monkeypatch.setenv("ARCH_BACKEND", "live")
    # No keys present -> LiveLLM is selected but transparently falls back.
    out = llm.chat([{"role": "user", "content": "hello"}], agent="hermes-core")
    assert isinstance(out, str) and len(out) > 0


def test_provider_resolution():
    assert llm._provider_for_model("gpt-4o") == "openai"
    assert llm._provider_for_model("gemini-2.0-flash") == "google"
    assert llm._provider_for_model("claude-sonnet-4-6") == "anthropic"
