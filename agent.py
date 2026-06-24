"""Generic EdVisingU specialist agent — one image, 25 personalities.

The fleet used to be 25 near-identical FastAPI apps. This single app replaces
them all: ``AGENT_NAME`` (env) selects which personality to load from
``souls/<name>.md`` and which model to route to (via core.fleet). It exposes
``/health`` and ``/chat`` and reasons through the shared LLM client, which
defaults to a zero-cost mock (no API key). Set ARCH_BACKEND=live + a key for
real models.

Run one agent locally:
    AGENT_NAME=hermes-finance uvicorn agent:app --port 8010
In production, docker-compose runs 25 containers off this one image, each with
its own AGENT_NAME and port.
"""

import os
import sys
from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel

_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from core import fleet
from core.llm import chat as llm_chat

AGENT_NAME = os.environ.get("AGENT_NAME", "hermes-core")


def _load_soul(name: str) -> str:
    path = fleet.soul_path(name)
    return path.read_text() if path.exists() else ""


SOUL = _load_soul(AGENT_NAME)

app = FastAPI(title=f"EdVisingU Agent — {AGENT_NAME}")


class ChatRequest(BaseModel):
    message: str
    history: list = []
    model: str = ""


@app.get("/health")
def health():
    return {"status": "ok", "agent": AGENT_NAME, "model": fleet.model_for(AGENT_NAME)}


@app.post("/chat")
async def chat(req: ChatRequest):
    messages = req.history + [{"role": "user", "content": req.message}]
    model = req.model or fleet.model_for(AGENT_NAME)
    response = llm_chat(messages, system=SOUL, model=model, agent=AGENT_NAME)
    return {"response": response, "agent": AGENT_NAME, "model": model}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
