#!/usr/bin/env python3
"""Agent Creation Framework — add any new agent in 4 steps (Manual Section 31).

The Jarvis system scales infinitely: every new specialist follows the same
4-step pattern (SOUL.md → app.py → Dockerfile → register). This generator
produces all four artifacts for a brand-new agent and prints the exact
registration lines for the router and docker-compose.

Usage
-----
    python scripts/new_agent.py <name> \
        --role "Grant Writer" \
        --model sonnet \
        --port 8028 \
        --capabilities "Draft grant applications" "Track funding deadlines"

``<name>`` may be given with or without the ``hermes-`` prefix. ``--model`` is
one of: sonnet (default), haiku, gemini, codex. Re-running is safe: existing
files are not overwritten unless ``--force`` is passed.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_AGENTS_DIR = _PROJECT_ROOT / "vps-agents" / "agents"

MODEL_GROUPS = {
    "sonnet": ("Claude Sonnet 4.6", None),
    "haiku": ("Claude Haiku 4.5", "HAIKU_AGENTS"),
    "gemini": ("Gemini 2.0 Flash", "GEMINI_AGENTS"),
    "codex": ("GPT-4o", "CODEX_AGENTS"),
}

DOCKERFILE = """FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
"""

REQUIREMENTS = """fastapi==0.115.0
uvicorn==0.30.6
anthropic==0.34.0
httpx==0.27.2
pydantic==2.9.0
python-dotenv==1.0.1
"""


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
- ChromaDB / Supabase via the shared store for relevant context.

## Model
{model_label}

## Owner
Dr. Andre De Freitas (andre@edvisingu.ca)
"""


def app_py(agent: str) -> str:
    """app.py mirrors the shipped agent template so it runs offline ($0)."""
    template = (_AGENTS_DIR / "hermes-core" / "app.py").read_text()
    return template.replace("hermes-core", agent)


def _rel(path: Path) -> str:
    try:
        return str(path.relative_to(_PROJECT_ROOT))
    except ValueError:
        return str(path)


def create_agent(name: str, role: str, model: str, capabilities: list[str],
                 force: bool = False) -> dict:
    if model not in MODEL_GROUPS:
        raise ValueError(f"model must be one of {sorted(MODEL_GROUPS)}")
    agent = normalize_name(name)
    model_label, group = MODEL_GROUPS[model]
    target = _AGENTS_DIR / agent
    target.mkdir(parents=True, exist_ok=True)

    files = {
        "SOUL.md": soul_md(agent, role, model_label, capabilities),
        "app.py": app_py(agent),
        "Dockerfile": DOCKERFILE,
        "requirements.txt": REQUIREMENTS,
    }
    written = []
    for fname, content in files.items():
        path = target / fname
        if path.exists() and not force:
            continue
        path.write_text(content)
        written.append(_rel(path))

    return {"agent": agent, "role": role, "model": model_label, "model_group": group,
            "dir": _rel(target), "written": written}


def registration_instructions(agent: str, model_group: str | None, port: int) -> str:
    group_line = (
        f"    {model_group}.add(\"{agent}\")  # in core/llm.py and fastapi-router"
        if model_group else "    # uses default Claude Sonnet — no model-group change needed"
    )
    return f"""Step 4 — register the agent:

1) fastapi-router/main.py  →  add to AGENT_PORTS:
       "{agent}": {port},

2) core/llm.py model group (only if not default Sonnet):
{group_line}

3) docker-compose.yml  →  add service block:
       {agent}:
         build: ./vps-agents/agents/{agent}
         container_name: {agent}
         restart: always
         ports: ["{port}:8000"]
         env_file: /opt/edvisingu/.env

Deploy & test:
   docker compose build {agent} && docker compose up -d {agent}
   curl http://localhost:{port}/health
   curl -X POST http://localhost:{port}/chat -H "Content-Type: application/json" \\
        -d '{{"message":"hello","history":[]}}'
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Add a new hermes agent (Manual Section 31).")
    parser.add_argument("name", help="agent name, with or without the hermes- prefix")
    parser.add_argument("--role", default="specialist", help="short role description")
    parser.add_argument("--model", default="sonnet", choices=sorted(MODEL_GROUPS))
    parser.add_argument("--port", type=int, default=8028, help="host port (next free after 8027)")
    parser.add_argument("--capabilities", nargs="*", default=[], help="capability bullet points")
    parser.add_argument("--force", action="store_true", help="overwrite existing files")
    args = parser.parse_args(argv)

    result = create_agent(args.name, args.role, args.model, args.capabilities, force=args.force)
    print(f"✅ Created {result['agent']} ({result['model']}) in {result['dir']}")
    for f in result["written"]:
        print(f"   + {f}")
    if not result["written"]:
        print("   (no files written — already exist; pass --force to overwrite)")
    print()
    print(registration_instructions(result["agent"], result["model_group"], args.port))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
