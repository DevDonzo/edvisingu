# Build Status — Master Build Manual → Code

Maps each section of the *EdVisingU AI Ecosystem Master Build Manual* to where it
lives in this repo and its state in **offline / $0 mode**. Everything marked
"Local mock" runs with no API key; the live path activates with `ARCH_BACKEND=live`
plus the relevant key.

| Manual section | Component | Where in repo | Status (offline / $0) |
|----------------|-----------|---------------|------------------------|
| 0 | OpenJarvis + hermes-agent gateway | `docs/` notes, README "Go live" | Documented (VPS-only; live deploy) |
| 1–5 | Folder structure, env, Phase 1 | repo layout, `.env.example`, `.gitignore` | Done |
| 6.1 | Ollama local models | (dropped) — agents reason via `core/llm.py` cloud SDKs | Not used; removed |
| 6.2 | ChromaDB vector memory | replaced by `core/store.py` `ai_memory` (SQLite) | Replaced — Chroma dropped (no code used it) |
| 6.3 | n8n automation | `automation/docker-compose.yml`, `tools/n8n_tools.py`, `workflows/` | Local mock trigger; workflows hit local API |
| 6.4 | FastAPI orchestration API | `router.py` (live) + `demo_server.py` (demo) | Done — runs offline via `core.llm` |
| 7 | Hermes agent + memory | `agent.py` + `souls/hermes-core.md`, `demo_server.py` `/hermes/chat` | Done (mock LLM; SQLite memory) |
| 8 | Database | **`core/store.py` (SQLite)**, `api-configs/schema.sql` | Done — local; Supabase not required |
| 9 | Content automation | `demo_server.py` `/content/generate`, `workflows/` | Done (persists to store) |
| 10 | Specialist agents (advisor, CrediHire, social) | `demo_server.py`, `agent.py` + `souls/*` | Done (mock) |
| 11 | Next.js dashboard (7 pages) | `dashboards/edvisingu-dashboard` | Done — 9 pages, `next build` clean |
| 12 | HeyGen / ElevenLabs / Whop / Discord | `demo_server.py` | Local mock (live behind keys) |
| 13 | Google AI tools | `core/llm.py` Gemini path | Live path ready; mock default |
| 14 | Security audit | `.gitignore`, key guards in `core/llm.py` + `tools/` | Done (no keys required/shipped) |
| 15 | Testing & QA | `tests/` (incl. `test_smoke.py`) | Done — 56 tests green, $0 |
| 16–19 | Deliverables / SOPs / timing | README, this file | Documented |
| 20 | Hermes Control Room (brain/body) | `agent.py` (one image) + `souls/*` (25 personalities) | Done (offline agents) |
| 20.6 / 24.7 | Agent Task Bus | `tools/task_bus.py`, `core/orchestrator.py` | Done — file queue (Redis behind live) |
| 20.8 / 22 / 26 | Multi-model router | `router.py`, `core/fleet.py` (roster+routing) | Done — offline fallback + routing matrix |
| 21 | Hetzner VPS setup | README "Go live on Hetzner", `monitoring/` | Documented (needs VPS) |
| 23 | Agent tools layer | `tools/{search,code_exec,file_tools,n8n,notion,stripe,github,task_bus}.py` | Done — all mock modes |
| 24 / 27 | Full 25-agent fleet | `core/fleet.py` + `souls/hermes-*.md` (1 image, 25 souls) | Done — all run offline |
| 25 | Monitoring (Uptime Kuma) | `demo_server.py` `/monitoring`, `dashboard/status`, `monitoring/` | Done — local health rollup |
| 28 | Google Workspace full API (Gmail, Calendar, Drive, Gemini grounding) | `tools/{gmail,calendar,gemini,drive}_tools.py` | Done — all mock; live behind `GOOGLE_REFRESH_TOKEN` / `GOOGLE_AI_API_KEY` |
| 29 | Platform Integrations Part 2 (Blotato, MailerLite, ManyChat, Disco.co) | `tools/{blotato,mailerlite,manychat,disco}_tools.py` | Done — all mock; live behind each key |
| 30 | DrDDurham political campaign automation | `demo_server.py` `/campaign/{brand,generate,schedule}`, `souls/hermes-campaign.md` | Done — weekly batch (7 FB / 5 TT / 3 IG / 2 email) + Canada Elections Act authorization line + compliance list |
| 31 | Agent creation framework (add any agent in 2 steps) | `scripts/new_agent.py` | Done — writes `souls/<name>.md` + prints the one-line `core/fleet.py` entry; everything else derives |

## Definition of done (met)

- `bash demo.sh` → full system locally, no keys, $0.
- `python run.py selftest` → green.
- `python -m pytest` → **56 passed**, no API key, no cost.
- `npx next build` → 13 routes compile (incl. advisor, credihire, analytics, status).

## Architecture (after consolidation)

Two deployments share one codebase, with `core/fleet.py` as the single source
of truth for the roster + model routing:

- **Local demo** — `demo_server.py` (all-in-one mock API) + `dashboards/` (Next.js).
  Run with `bash demo.sh`.
- **Live VPS** — `router.py` (OpenAI-compatible multi-model router) in front of
  the 25-agent fleet. The fleet is **one** image (`agent.py` + `Dockerfile.agent`)
  run as 25 containers, each selecting its personality from `souls/<name>.md` via
  `AGENT_NAME`. Run with `bash scripts/start.sh` (router) or `docker compose up`.

Both reason through `core/llm.py` and persist to `core/store.py` (SQLite).
Removed as redundant: the standalone orchestration API (`agents/main.py`), the
legacy LangChain/Ollama Hermes (`agents/hermes/`), the 25 duplicate agent dirs
(collapsed to one image + `souls/`), and the unused ChromaDB + Supabase layers.
SQLite is the single data + memory layer; `core/fleet.py` is the single roster.

## What is intentionally NOT executed (requires money/accounts)

- Provisioning a real Hetzner VPS, real n8n cloud, real
  Whop/Stripe/HeyGen/ElevenLabs/Tavily accounts.
- These are fully **documented** (README "Go live on Hetzner") and the code path
  is ready: set the key + `ARCH_BACKEND=live`. No code changes needed.
