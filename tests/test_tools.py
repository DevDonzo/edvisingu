"""Tests for the agent tools layer — all offline/mock ($0, no keys)."""

import pytest

from tools import search, stripe_tools, n8n_tools, notion_tools, github_tools, file_tools, code_exec, is_live


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    monkeypatch.delenv("ARCH_BACKEND", raising=False)
    for k in ("TAVILY_API_KEY", "STRIPE_SECRET_KEY", "NOTION_TOKEN", "GITHUB_TOKEN"):
        monkeypatch.delenv(k, raising=False)


def test_is_live_default_false():
    assert is_live() is False
    assert is_live("TAVILY_API_KEY") is False


def test_web_search_mock():
    out = search.web_search("ai tools for students", max_results=3)
    assert out["mock"] is True and len(out["results"]) == 3
    assert out["results"][0]["url"].startswith("https://")


def test_stripe_mock():
    assert stripe_tools.get_mrr()["mrr"] == 4230.0
    assert stripe_tools.get_recent_revenue(7)["days"] == 7


def test_n8n_mock():
    out = n8n_tools.trigger_content_pipeline("topic", "linkedin")
    assert out["mock"] is True and out["status"] == 200


def test_notion_mock():
    out = notion_tools.create_notion_page("parent", "My Page", "body")
    assert out["mock"] is True and out["url"].startswith("https://notion.so/")


def test_github_mock():
    out = github_tools.create_repo("test-repo", "desc")
    assert out["mock"] is True and "test-repo" in out["url"]


def test_file_tool_writes_locally(tmp_path, monkeypatch):
    monkeypatch.setenv("SHARED_FILES_DIR", str(tmp_path))
    out = file_tools.create_file("note.txt", "hello", subfolder="research")
    assert out["size"] == 5
    assert out["path"].endswith("research/note.txt")


def test_code_exec_real_sandbox():
    out = code_exec.run_python_code("print(2 + 2)")
    assert out["returncode"] == 0 and out["stdout"].strip() == "4"
