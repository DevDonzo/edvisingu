#!/usr/bin/env python3
"""Agent Creation Framework — add any new agent in 2 steps (Manual Section 31).

Since the fleet was consolidated to a single shared image, adding an agent no
longer means copying app.py/Dockerfile/requirements. It is now:

  Step 1  write souls/<name>.md  (this script does it)
  Step 2  add one Agent(...) line to core/fleet.py  (this script prints it)

docker-compose, the router, the dashboard fleet view, model routing and the CLI
all derive from core.fleet automatically — there is nowhere else to edit.

Usage
-----
    python scripts/new_agent.py grants \\
        --role "Grant Writer" --model haiku --port 8028 \\
        --capabilities "Draft grant applications" "Track funding deadlines"

``<name>`` may be given with or without the ``hermes-`` prefix. ``--model`` is
one of: sonnet (default), haiku, gemini, codex. Re-running won't overwrite an
existing soul unless ``--force`` is passed.
"""

from __future__ import annotations

import argparse
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_SOULS_DIR = _PROJECT_ROOT / "souls"

# label + canonical model id + core.fleet constant name
MODELS = {
    "sonnet": ("Claude Sonnet 4.6", "SONNET"),
    "haiku": ("Claude Haiku 4.5", "HAIKU"),
    "gemini": ("Gemini 2.0 Flash", "GEMINI"),
    "codex": ("GPT-4o", "GPT4O"),
}


def normalize_name(name: str) -> str:
    name = name.strip().lower().replace(" ", "-")
    return name if name.startswith("hermes-") else f"hermes-{name}"


def soul_md(agent: str, role: str, model_label: str, capabilities: list[str]) -> str:
    caps = "\n".join(f"- {c}" for c in capabilities) or "- [3-5 specific tasks this agent does]"
    return f"""# SOUL — {agent}

## Identity
You are **{agent}**, Dr. D's {role}.

## Mission
Deliver {role.lower()} outcomes for the EdVisingU ecosystem with clear,
on-brand, review-ready output.

## Capabilities
{caps}

## Rules
- Never send, publish, or spend without explicit human approval.
- Stay within your specialty; hand off anything out of scope to hermes-core.
- Keep all output on-brand and compliant.

## Integrations
- Shared core.llm client (mock by default; live behind ARCH_BACKEND=live)
- Agent Task Bus (file queue; Redis in production)

## Memory
- Local SQLite store (core/store.py) for relevant context.

## Model
{model_label}

## Owner
Dr. Andre De Freitas (andre@edvisingu.ca)
"""


def create_agent(name: str, role: str, model: str, capabilities: list[str],
                 force: bool = False) -> dict:
    if model not in MODELS:
        raise ValueError(f"model must be one of {sorted(MODELS)}")
    agent = normalize_name(name)
    model_label, fleet_const = MODELS[model]
    _SOULS_DIR.mkdir(parents=True, exist_ok=True)
    path = _SOULS_DIR / f"{agent}.md"

    written = False
    if force or not path.exists():
        path.write_text(soul_md(agent, role, model_label, capabilities))
        written = True

    try:
        rel = str(path.relative_to(_PROJECT_ROOT))
    except ValueError:
        rel = str(path)

    return {"agent": agent, "role": role, "model": model_label,
            "fleet_const": fleet_const, "soul": rel, "written": written}


def registration_line(agent: str, role: str, fleet_const: str, port: int) -> str:
    return (
        f'    Agent("{agent}", {port}, {fleet_const}, "{role}", "core"),'
        f'   # <-- add this to FLEET in core/fleet.py (pick the right category)'
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Add a new hermes agent (Manual Section 31).")
    parser.add_argument("name", help="agent name, with or without the hermes- prefix")
    parser.add_argument("--role", default="specialist", help="short role description")
    parser.add_argument("--model", default="sonnet", choices=sorted(MODELS))
    parser.add_argument("--port", type=int, default=8028, help="host port (next free after 8027)")
    parser.add_argument("--capabilities", nargs="*", default=[], help="capability bullet points")
    parser.add_argument("--force", action="store_true", help="overwrite an existing soul")
    args = parser.parse_args(argv)

    r = create_agent(args.name, args.role, args.model, args.capabilities, force=args.force)
    if r["written"]:
        print(f"✅ Step 1 done — wrote {r['soul']} ({r['model']})")
    else:
        print(f"• Step 1 skipped — {r['soul']} already exists (use --force to overwrite)")
    print()
    print("Step 2 — register it in the fleet (single source of truth):")
    print(registration_line(r["agent"], r["role"], r["fleet_const"], args.port))
    print()
    print("That's it. docker-compose, router, dashboard, routing and the CLI all")
    print("pick it up from core.fleet. Test locally:")
    print(f'   AGENT_NAME={r["agent"]} uvicorn agent:app --port {args.port}')
    print(f"   curl http://localhost:{args.port}/health")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
