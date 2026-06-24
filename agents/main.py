"""EdVisingU AI Orchestration API (Manual Sections 6.4, 7.4, 10, 12, 20.8).

Refactored to run offline at $0: all reasoning goes through ``core.llm`` (mock
by default), data persists in the local SQLite store, and paid integrations
(HeyGen, ElevenLabs) return realistic mocks unless their key is present.
"""

import os
import sys
from pathlib import Path

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from core import store
from core.llm import chat as llm_chat, model_for_agent


@asynccontextmanager
async def lifespan(app: FastAPI):
    store.ensure_seeded()
    yield


app = FastAPI(title="EdVisingU AI Orchestration API", version="2.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request Models ────────────────────────────────────

class ChatRequest(BaseModel):
    message: str
    model: str = ""
    agent: str = "hermes-core"
    history: list = []
    max_tokens: int = 2048


class ContentRequest(BaseModel):
    topic: str
    platforms: list[str] = ["linkedin", "tiktok", "email"]
    tone: str = "bold, direct, and insightful"


class ResumeRequest(BaseModel):
    resume_text: str
    job_description: str = ""


class HeyGenRequest(BaseModel):
    script: str
    avatar_id: str = "demo-avatar"


class TTSRequest(BaseModel):
    text: str
    voice_id: str = "demo-voice"


# ── Agent Fleet (Manual Section 20.8 / 26) ────────────

AGENT_ROUTES = {
    "hermes-core": "http://hermes-core:8000",
    "hermes-content": "http://hermes-content:8000",
    "hermes-advisor": "http://hermes-advisor:8000",
    "hermes-credihire": "http://hermes-credihire:8000",
    "hermes-ops": "http://hermes-ops:8000",
    "hermes-social": "http://hermes-social:8000",
    "hermes-builder": "http://hermes-builder:8000",
    "hermes-research": "http://hermes-research:8000",
    "hermes-finance": "http://hermes-finance:8000",
    "hermes-email": "http://hermes-email:8000",
}

HERMES_SYSTEM = """You are Hermes, the AI Executive Assistant for Dr. Andre De Freitas (Dr. D),
founder of EdVisingU, CrediVersity, DrD Learn, and HireEd Nexus Labs. Be direct, specific, and
execution-focused. Tie outputs to revenue, efficiency, or growth."""

ADVISOR_SYSTEM = """You are the EdVisingU Student AI Advisor. Help students succeed academically,
earn income while studying, and build career-ready skills. Always recommend specific EdVisingU
programs, HireEd Nexus Labs opportunities, or CrediVersity credentials. Be encouraging, action-
oriented, and specific."""


# ── Core Endpoints ────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "running", "version": "2.0.0", "ecosystem": "EdVisingU"}


@app.post("/chat")
async def chat(req: ChatRequest):
    messages = req.history + [{"role": "user", "content": req.message}]
    model = req.model or model_for_agent(req.agent)
    text = llm_chat(messages, model=model, agent=req.agent)
    return {"response": text, "model": model, "agent": req.agent}


@app.post("/content/generate")
async def generate_content(req: ContentRequest):
    prompt = (
        f"You are Dr. Andre De Freitas, founder of EdVisingU. Write content about: {req.topic}\n"
        f"Tone: {req.tone}\nGenerate for platforms: {', '.join(req.platforms)}.\n"
        "Return platform-optimized copy following each platform's best practices."
    )
    out = {}
    for platform in req.platforms:
        out[platform] = llm_chat(
            [{"role": "user", "content": f"{prompt}\n\nPlatform: {platform}"}],
            agent="hermes-content",
        )
        store.insert_content(req.topic, platform, raw_content=out[platform], status="pending")
    return {"topic": req.topic, "content": out, "platforms_generated": len(out)}


# ── Hermes ────────────────────────────────────────────

@app.post("/hermes/chat")
async def hermes_endpoint(req: ChatRequest):
    messages = req.history + [{"role": "user", "content": req.message}]
    text = llm_chat(messages, system=HERMES_SYSTEM, agent="hermes-core")
    return {"response": text, "agent": "hermes"}


# ── Student Advisor ───────────────────────────────────

@app.post("/advisor/chat")
async def advisor_chat(req: ChatRequest):
    messages = req.history + [{"role": "user", "content": req.message}]
    text = llm_chat(messages, system=ADVISOR_SYSTEM, agent="hermes-advisor")
    return {"response": text, "agent": "student-advisor"}


# ── CrediHire Resume Agent ────────────────────────────

@app.post("/credihire/analyze")
async def analyze_resume(req: ResumeRequest):
    prompt = (
        "Analyze this resume for ATS compatibility and overall strength. Return ats_score (0-100), "
        f"strengths, weaknesses, and improvements.\nResume:\n{req.resume_text}"
    )
    return {"analysis": llm_chat([{"role": "user", "content": prompt}], agent="hermes-credihire")}


@app.post("/credihire/optimize")
async def optimize_resume(req: ResumeRequest):
    prompt = (
        "Rewrite this resume optimized for ATS and the target job description.\n"
        f"Resume:\n{req.resume_text}\n\nJob Description:\n{req.job_description}"
    )
    return {"optimized_resume": llm_chat([{"role": "user", "content": prompt}], agent="hermes-credihire")}


@app.post("/credihire/cover-letter")
async def cover_letter(req: ResumeRequest):
    prompt = (
        "Generate a targeted cover letter from this resume for the job posting.\n"
        f"Resume:\n{req.resume_text}\n\nJob Posting:\n{req.job_description}"
    )
    return {"cover_letter": llm_chat([{"role": "user", "content": prompt}], agent="hermes-credihire")}


# ── HeyGen / ElevenLabs (mock unless key present) ─────

@app.post("/heygen/generate")
async def heygen_video(req: HeyGenRequest):
    if os.getenv("HEYGEN_API_KEY") and os.getenv("ARCH_BACKEND") == "live":  # pragma: no cover
        import httpx

        url = "https://api.heygen.com/v2/video/generate"
        headers = {"X-Api-Key": os.getenv("HEYGEN_API_KEY"), "Content-Type": "application/json"}
        payload = {
            "video_inputs": [{
                "character": {"type": "avatar", "avatar_id": req.avatar_id},
                "voice": {"type": "text", "input_text": req.script, "speed": 1.0},
            }],
            "dimension": {"width": 1080, "height": 1920},
            "aspect_ratio": "9:16",
        }
        async with httpx.AsyncClient() as client:
            r = await client.post(url, json=payload, headers=headers)
        return r.json()
    return {
        "mock": True,
        "video_id": f"mock_vid_{abs(hash(req.script)) % 100000}",
        "status": "processing",
        "avatar_id": req.avatar_id,
        "note": "Mock HeyGen job. Set HEYGEN_API_KEY + ARCH_BACKEND=live for real video.",
    }


@app.post("/elevenlabs/speak")
async def text_to_speech(req: TTSRequest):
    if os.getenv("ELEVENLABS_API_KEY") and os.getenv("ARCH_BACKEND") == "live":  # pragma: no cover
        from elevenlabs.client import ElevenLabs

        client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
        audio = client.generate(text=req.text, voice=req.voice_id, model="eleven_monolingual_v1")
        path = f"/tmp/audio_{abs(hash(req.text)) % 100000}.mp3"
        with open(path, "wb") as f:
            for chunk in audio:
                f.write(chunk)
        return {"audio_path": path, "voice_id": req.voice_id}
    return {
        "mock": True,
        "audio_path": f"/tmp/mock_audio_{abs(hash(req.text)) % 100000}.mp3",
        "voice_id": req.voice_id,
        "note": "Mock ElevenLabs output. Set ELEVENLABS_API_KEY + ARCH_BACKEND=live for real audio.",
    }


# ── Agent Fleet Router (Manual Section 20.8) ──────────

@app.post("/agent/{agent_name}/chat")
async def route_to_agent(agent_name: str, req: ChatRequest):
    """Route to a specialist. Tries the container; falls back to in-process mock."""
    messages = req.history + [{"role": "user", "content": req.message}]
    model = model_for_agent(agent_name)
    # Local/offline: answer in-process via the shared LLM (no container needed).
    if os.getenv("ARCH_BACKEND") == "live" and agent_name in AGENT_ROUTES:  # pragma: no cover
        import httpx

        try:
            async with httpx.AsyncClient(timeout=60) as client:
                r = await client.post(f"{AGENT_ROUTES[agent_name]}/chat", json=req.model_dump())
            return r.json()
        except Exception:
            pass
    text = llm_chat(messages, model=model, agent=agent_name)
    return {"response": text, "agent": agent_name, "model": model}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
