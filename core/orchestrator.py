"""Orchestrator demo (Manual Section 20.6).

Shows the hub-and-spoke handoff: the orchestrator (hermes-core) decomposes a
request into a subtask and publishes it to the Task Bus; a specialist agent
picks it up, processes it via the shared (mock) LLM, and writes the result to
the outbox; the orchestrator reads the outbox and returns a synthesis. Runs at
$0 with no keys.
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from core.llm import chat, model_for_agent
from tools import task_bus


def dispatch(message: str, agent: str = "hermes-content", action: str = "process_request") -> dict:
    """Run one request through the full inbox -> working -> outbox lifecycle."""
    # 1. Orchestrator publishes a subtask to the specialist's inbox.
    queued = task_bus.publish_task(agent, action, {"message": message})
    task_id = queued["task_id"]

    # 2. Specialist picks it up (inbox -> working).
    task = task_bus.get_next_task(agent)
    if task is None:
        return {"error": "task not found in inbox", "task_id": task_id}

    # 3. Specialist processes the work via the shared LLM (mock by default).
    answer = chat(
        [{"role": "user", "content": task["payload"]["message"]}],
        model=model_for_agent(agent),
        agent=agent,
    )

    # 4. Specialist writes the result to the outbox (working -> outbox).
    completed = task_bus.complete_task(task_id, {"agent": agent, "answer": answer})

    # 5. Orchestrator reads the outbox and synthesizes.
    out = task_bus.read_outbox(task_id)
    return {
        "task_id": task_id,
        "agent": agent,
        "model": model_for_agent(agent),
        "status": completed["status"],
        "stages": ["inbox", "working", "outbox"],
        "result": out["result"] if out else None,
    }


if __name__ == "__main__":
    import json

    result = dispatch("Write a LinkedIn hook about AI tools for Canadian students")
    print(json.dumps(result, indent=2))
