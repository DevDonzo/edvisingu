# EdVisingU AI Ecosystem

An AI operating system from the **EdVisingU Master Build Manual** — a 25-agent
fleet, content factory, student advisor, resume engine, CRM, and monitoring.

This repository runs **fully offline at $0 with no API keys**. Every paid service
in the manual (Claude/OpenAI/Gemini, Supabase, Stripe, Tavily, n8n, Whop, HeyGen,
ElevenLabs, Redis) has a deterministic local mock. The exact same code goes live
on a Hetzner VPS later by adding keys and flipping one environment variable.

---

## Quickstart — offline, $0, no keys

```bash
cd edvisingu
python3 -m venv venv && source venv/bin/activate   # first time only
pip install -r requirements.txt                     # first time only — 6 packages, no torch/SDK bloat

bash demo.sh        # API on :8000 + dashboard on :3000
```

Offline needs just six packages (FastAPI, Uvicorn, Pydantic, httpx, python-dotenv,
pytest). Every paid SDK is lazy-loaded behind `ARCH_BACKEND=live`, so the live-only
extras live in `requirements-live.txt` and are installed only when you go live.

Open **http://localhost:3000/dashboard**. Swagger lives at **http://localhost:8000/docs**.

### CLI (no server needed)

```bash
python run.py selftest                              # prove it runs with $0
python run.py chat "what's our MRR?" --agent hermes-finance
python run.py content "AI tools for Canadian students"
python run.py taskbus "write a LinkedIn hook"       # Agent Task Bus demo
python run.py fleet                                 # 25 agents + model routing
```

### Tests

```bash
python -m pytest        # 59 tests, all green, no API key, no cost
```

---

## How offline mode works

| Manual component | Paid in manual | Local $0 stand-in |
|------------------|----------------|-------------------|
| Claude / GPT-4o / Gemini | API keys | `core/llm.py` `MockLLM` (deterministic) |
| Supabase / Postgres | hosted DB | `core/store.py` SQLite (`data/edvisingu.db`) |
| Stripe / Tavily / Notion / GitHub / n8n | API keys | `tools/*` mock modes |
| Redis task bus | Redis server | file queue `data/agent-bus/{inbox,working,outbox}` |
| HeyGen / ElevenLabs | API keys | mock job IDs / audio paths |

The switch is the `ARCH_BACKEND` environment variable:

- `ARCH_BACKEND=mock` (default) — everything is local and free.
- `ARCH_BACKEND=live` — real providers are used **only** where a matching key is
  present; anything missing transparently falls back to the mock (never crashes,
  never spends silently).

---

## Architecture

```
Dashboard (Next.js :3000)
        │  HTTP
        ▼
demo_server.py (:8000)  ── core/store.py (SQLite)
        │
        ├── core/llm.py        shared LLM client (mock | live)
        ├── core/orchestrator.py + tools/task_bus.py   Agent Task Bus
        └── 25 specialist agents (vps-agents/agents/hermes-*)
                routed by model (Sonnet / Haiku / Gemini / GPT-4o)
```

See `docs/BUILD_STATUS.md` for a section-by-section map of the manual to the code.

---

## Going live on Hetzner (Manual Section 21)

When you have a VPS and keys, the manual's production path is:

1. **Provision** a Hetzner CPX41 (8 vCPU / 16 GB) running Ubuntu 22.04.
2. **Harden**: create a `deploy` user, disable root/password SSH, enable UFW + fail2ban (Section 21.3).
3. **Install Docker** (Section 21.4) and optionally OpenJarvis + Tailscale.
4. **Clone** this repo to `/opt/edvisingu`.
5. **Install live extras** (on top of the offline core):
   `pip install -r requirements.txt -r requirements-live.txt`
6. **Add keys** to `/opt/edvisingu/.env` (copy `.env.example`):
   - `ANTHROPIC_API_KEY` (Claude — covers most agents)
   - `OPENAI_API_KEY` (GPT-4o — hermes-builder)
   - `GOOGLE_AI_API_KEY` (Gemini — social/SEO/TikTok/ads/pinterest)
   - plus `STRIPE_SECRET_KEY`, `TAVILY_API_KEY`, `NOTION_TOKEN`, `GITHUB_TOKEN`,
     `WHOP_API_KEY`, `HEYGEN_API_KEY`, `ELEVENLABS_API_KEY` as needed.
7. **Flip the switch**: `export ARCH_BACKEND=live`.
8. **Run**: `bash scripts/start.sh` (multi-model router + n8n) or the full
   `docker compose` fleet (Manual Section 20.7 / 24.6).
9. **Reverse proxy + SSL** via Nginx + Certbot (Section 21.6); **monitor** with
   Uptime Kuma (Section 25).

No code changes are required to go live — only keys and `ARCH_BACKEND=live`.

---

## Security

- `.env` is gitignored; never commit secrets. Store credentials in Bitwarden (Manual 1.4 / 14).
- The repo ships **no keys** and requires none to run.
- Network-exposed services (FastAPI, n8n, dashboard) ship without auth for local
  development — add authentication and restrict ports before exposing them publicly.
