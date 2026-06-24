"""Agent Task Bus (Manual 20.6 / 24.7).

The handoff desk between the orchestrator (hermes-core) and specialist agents.
Default ($0, offline): a directory-based queue at ``data/agent-bus`` with
``inbox/`` -> ``working/`` -> ``outbox/`` stages. Live mode (ARCH_BACKEND=live)
uses Redis if available.

Task file format (Manual 20.6):
    {task_id, agent, action, payload, priority, created_at, status, result}
"""

import json
import os
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

from tools import is_live

_PROJECT_ROOT = Path(__file__).resolve().parent.parent


def bus_dir() -> Path:
    return Path(os.environ.get("AGENT_BUS_DIR", str(_PROJECT_ROOT / "data" / "agent-bus")))


def _stage(name: str) -> Path:
    d = bus_dir() / name
    d.mkdir(parents=True, exist_ok=True)
    return d


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# File-based queue (default, $0)
# ---------------------------------------------------------------------------

def publish_task(agent: str, action: str, payload: dict, priority: str = "normal") -> dict:
    """Orchestrator writes a task to inbox/."""
    task_id = f"task-{int(time.time())}-{uuid.uuid4().hex[:6]}"
    task = {
        "task_id": task_id,
        "agent": agent,
        "action": action,
        "payload": payload,
        "priority": priority,
        "created_at": _now(),
        "status": "queued",
    }
    if is_live() and _redis_ready():  # pragma: no cover - needs redis
        _redis().lpush(f"tasks:{agent}", json.dumps(task))
    else:
        (_stage("inbox") / f"{task_id}.json").write_text(json.dumps(task, indent=2))
    return {"queued": True, "agent": agent, "task_id": task_id}


def get_next_task(agent_name: str) -> dict | None:
    """Specialist picks up the oldest queued task for it (inbox -> working)."""
    if is_live() and _redis_ready():  # pragma: no cover - needs redis
        raw = _redis().rpop(f"tasks:{agent_name}")
        return json.loads(raw) if raw else None
    inbox = _stage("inbox")
    candidates = sorted(
        p for p in inbox.glob("*.json")
        if json.loads(p.read_text()).get("agent") == agent_name
    )
    if not candidates:
        return None
    src = candidates[0]
    task = json.loads(src.read_text())
    task["status"] = "working"
    dest = _stage("working") / src.name
    dest.write_text(json.dumps(task, indent=2))
    src.unlink()
    return task


def complete_task(task_id: str, result) -> dict:
    """Specialist writes the result to outbox/ (working -> outbox)."""
    working = _stage("working")
    src = working / f"{task_id}.json"
    task = json.loads(src.read_text()) if src.exists() else {"task_id": task_id}
    task["status"] = "completed"
    task["result"] = result
    task["completed_at"] = _now()
    (_stage("outbox") / f"{task_id}.json").write_text(json.dumps(task, indent=2))
    if src.exists():
        src.unlink()
    return task


def read_outbox(task_id: str) -> dict | None:
    p = _stage("outbox") / f"{task_id}.json"
    return json.loads(p.read_text()) if p.exists() else None


def clear() -> None:
    """Remove all task files from every stage (test helper)."""
    for stage in ("inbox", "working", "outbox"):
        for p in _stage(stage).glob("*.json"):
            p.unlink()


# ---------------------------------------------------------------------------
# Redis backend (live only)
# ---------------------------------------------------------------------------

def _redis():  # pragma: no cover - needs redis
    import redis

    return redis.from_url(os.environ.get("REDIS_URL", "redis://redis:6379"))


def _redis_ready() -> bool:  # pragma: no cover - needs redis
    try:
        _redis().ping()
        return True
    except Exception:
        return False
