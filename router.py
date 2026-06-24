"""EdVisingU multi-model router (Manual Sections 22 & 26).

OpenAI-compatible facade in front of the 25-agent fleet. Offline ($0) it
answers in-process via ``core.llm`` (mock); with ARCH_BACKEND=live it forwards
to the agent containers. The roster comes from core.fleet (single source).
"""

import os
import sys
import time
from pathlib import Path

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from core.llm import chat as llm_chat, model_for_agent  # noqa: E402
from core.fleet import ports as _fleet_ports  # noqa: E402

app = FastAPI(title="EdVisingU Router")

AGENT_PORTS = _fleet_ports()  # single source of truth (core.fleet)


def _live() -> bool:
    return os.environ.get("ARCH_BACKEND", "mock").lower() == "live"


@app.get("/health")
def health():
    return {"status": "ok", "agents": len(AGENT_PORTS), "backend": "live" if _live() else "mock"}


@app.get("/v1/models")
def list_models():
    data = [
        {"id": name, "object": "model", "owned_by": "edvisingu", "model": model_for_agent(name)}
        for name in AGENT_PORTS
    ]
    return {"object": "list", "data": data}


@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    body = await request.json()
    model = body.get("model", "")
    agent = model if model in AGENT_PORTS else "hermes-core"
    messages = body.get("messages", [])
    backend_model = model_for_agent(agent)

    reply = None
    if _live():  # pragma: no cover - requires running containers/keys
        upstream = f"http://{agent}:8000/chat"
        last = messages[-1]["content"] if messages else ""
        history = messages[:-1]
        try:
            async with httpx.AsyncClient(timeout=120) as client:
                r = await client.post(upstream, json={"message": last, "history": history})
                reply = r.json().get("response")
        except Exception:
            reply = None

    if reply is None:
        # Offline / fallback: answer in-process via the shared mock LLM.
        reply = llm_chat(messages, model=backend_model, agent=agent)

    return JSONResponse({
        "id": f"chatcmpl-{agent}-{int(time.time())}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": backend_model,
        "choices": [{
            "index": 0,
            "message": {"role": "assistant", "content": reply},
            "finish_reason": "stop",
        }],
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
    })


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
