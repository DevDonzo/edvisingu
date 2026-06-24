#!/usr/bin/env python3
"""EdVisingU AI Ecosystem — offline CLI ($0, no keys required).

Examples:
    python run.py selftest
    python run.py chat "what's our MRR?" --agent hermes-finance
    python run.py content "AI tools for students"
    python run.py taskbus "write a LinkedIn hook"
    python run.py fleet
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from core import store
from core.llm import backend, chat, model_for_agent


def cmd_selftest(_args):
    print("Backend:", backend(), "(mock = $0, no API key)")
    store.ensure_seeded()
    print("Store stats:", json.dumps(store.stats(), indent=2))
    reply = chat([{"role": "user", "content": "give me a strategic overview"}], agent="hermes-core")
    print("\nhermes-core says:\n" + reply)
    print("\nOK — system runs offline with no keys.")


def cmd_chat(args):
    reply = chat([{"role": "user", "content": args.message}],
                 model=model_for_agent(args.agent), agent=args.agent)
    print(f"[{args.agent} · {model_for_agent(args.agent)}]\n{reply}")


def cmd_content(args):
    platforms = args.platforms.split(",")
    for p in platforms:
        text = chat([{"role": "user", "content": f"Write {p} content about: {args.topic}"}],
                    agent="hermes-content")
        store.insert_content(args.topic, p, raw_content=text, status="pending")
        print(f"\n===== {p.upper()} =====\n{text}")


def cmd_taskbus(args):
    from core import orchestrator
    result = orchestrator.dispatch(args.message, agent=args.agent)
    print(json.dumps(result, indent=2))


def cmd_fleet(_args):
    from core.llm import CODEX_AGENTS, GEMINI_AGENTS, HAIKU_AGENTS
    agents = sorted(set(
        ["hermes-core", "hermes-content", "hermes-advisor", "hermes-credihire", "hermes-ops",
         "hermes-social", "hermes-builder", "hermes-research", "hermes-finance", "hermes-email",
         "hermes-ads", "hermes-seo", "hermes-funnel", "hermes-etsy", "hermes-outreach",
         "hermes-proposals", "hermes-crm", "hermes-crediversity", "hermes-hireed",
         "hermes-educonnect", "hermes-whop", "hermes-tiktok", "hermes-campaign",
         "hermes-gumroad", "hermes-pinterest"]
    ))
    print(f"{len(agents)} agents:")
    for a in agents:
        print(f"  {a:22s} -> {model_for_agent(a)}")


def main():
    parser = argparse.ArgumentParser(description="EdVisingU offline CLI ($0, no keys)")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("selftest", help="Verify the system runs offline")

    p_chat = sub.add_parser("chat", help="Chat with an agent")
    p_chat.add_argument("message")
    p_chat.add_argument("--agent", default="hermes-core")

    p_content = sub.add_parser("content", help="Generate platform content")
    p_content.add_argument("topic")
    p_content.add_argument("--platforms", default="linkedin,tiktok,email")

    p_task = sub.add_parser("taskbus", help="Run a task through the Agent Task Bus")
    p_task.add_argument("message")
    p_task.add_argument("--agent", default="hermes-content")

    sub.add_parser("fleet", help="List the 25-agent fleet and model routing")

    args = parser.parse_args()
    handlers = {
        "selftest": cmd_selftest, "chat": cmd_chat, "content": cmd_content,
        "taskbus": cmd_taskbus, "fleet": cmd_fleet,
    }
    if args.cmd not in handlers:
        parser.print_help()
        return
    handlers[args.cmd](args)


if __name__ == "__main__":
    main()
