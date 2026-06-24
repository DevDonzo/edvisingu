"""EdVisingU specialist agent — runs offline ($0) via core.llm.

Each agent is a tiny FastAPI app exposing /health and /chat. It loads its
personality from SOUL.md and routes reasoning through the shared LLM client,
which defaults to a zero-cost mock (no API key required). Set ARCH_BACKEND=live
plus the relevant key to use real models.
"""

import os
import sys
from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel

# Make the shared `core` package importable whether this runs locally from the
# repo or inside its Docker container.
_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

try:
    from core.llm import chat as llm_chat, model_for_agent
except Exception:  # pragma: no cover - only if core is missing
    llm_chat = None

    def model_for_agent(_):
        return "mock"


AGENT_NAME = "hermes-educonnect"


def _load_soul() -> str:
    """SOUL.md lives at /data in the container, or beside this file locally."""
    for candidate in ("/data/SOUL.md", str(Path(__file__).resolve().parent / "SOUL.md")):
        if os.path.exists(candidate):
            with open(candidate) as fh:
                return fh.read()
    return ""


SOUL = _load_soul()

app = FastAPI(title=f"EdVisingU Agent — {AGENT_NAME}")


class ChatRequest(BaseModel):
    message: str
    history: list = []
    model: str = ""


@app.get("/health")
def health():
    return {"status": "ok", "agent": AGENT_NAME, "model": model_for_agent(AGENT_NAME)}


@app.post("/chat")
async def chat(req: ChatRequest):
    messages = req.history + [{"role": "user", "content": req.message}]
    model = req.model or model_for_agent(AGENT_NAME)
    if llm_chat is None:
        return {"response": f"[{AGENT_NAME}] core.llm unavailable", "agent": AGENT_NAME, "model": model}
    response = llm_chat(messages, system=SOUL, model=model, agent=AGENT_NAME)
    return {"response": response, "agent": AGENT_NAME, "model": model}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
