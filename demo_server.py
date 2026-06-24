"""AI Command Center — Local Demo Server
Rich mock responses that demonstrate the full system architecture.
Built by Hamza Paracha."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timedelta
import os, sys, random, time, asyncio
from pathlib import Path

# Make the shared `core` package importable and seed the local SQLite store.
_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
from core import store
store.ensure_seeded()

app = FastAPI(title="AI Command Center", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# ── Models ────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str
    agent: str = "hermes-core"

class ResumeRequest(BaseModel):
    resume_text: str = ""
    job_description: str = ""

class HeyGenRequest(BaseModel):
    script: str
    avatar_id: str = "demo-avatar"

class TTSRequest(BaseModel):
    text: str
    voice_id: str = "demo-voice"

class WhopEvent(BaseModel):
    event: str = "member.created"
    email: str
    name: str = ""
    plan: str = "standard"
    whop_id: str = ""

class ContentRequest(BaseModel):
    topic: str
    platforms: list[str] = ["linkedin", "tiktok", "email"]

class CampaignRequest(BaseModel):
    theme: str = "Week's events and local Pickering news"
    week_of: str = ""

class CampaignScheduleRequest(BaseModel):
    post_ids: list[str] = []
    scheduled_at: str = ""

# ── Agent Fleet Config ────────────────────────────────

FLEET = [
    {"name": "hermes-core", "port": 8001, "model": "Claude Sonnet 4.6", "role": "Executive Assistant", "status": "online", "category": "core"},
    {"name": "hermes-content", "port": 8002, "model": "Claude Sonnet 4.6", "role": "Content Factory", "status": "online", "category": "content"},
    {"name": "hermes-advisor", "port": 8003, "model": "Claude Sonnet 4.6", "role": "Student Advisor", "status": "online", "category": "education"},
    {"name": "hermes-credihire", "port": 8004, "model": "Claude Sonnet 4.6", "role": "Resume & Career", "status": "online", "category": "education"},
    {"name": "hermes-ops", "port": 8005, "model": "Claude Haiku 4.5", "role": "System Monitor", "status": "online", "category": "ops"},
    {"name": "hermes-social", "port": 8006, "model": "Claude Sonnet 4.6", "role": "Community Manager", "status": "online", "category": "content"},
    {"name": "hermes-builder", "port": 8008, "model": "GPT-4o", "role": "Project Builder", "status": "online", "category": "dev"},
    {"name": "hermes-research", "port": 8009, "model": "Claude Sonnet 4.6", "role": "Intelligence", "status": "online", "category": "core"},
    {"name": "hermes-finance", "port": 8010, "model": "Claude Haiku 4.5", "role": "Revenue Tracker", "status": "online", "category": "ops"},
    {"name": "hermes-email", "port": 8011, "model": "Claude Sonnet 4.6", "role": "Communications", "status": "online", "category": "core"},
    {"name": "hermes-ads", "port": 8012, "model": "Gemini 2.0 Flash", "role": "Ad Strategist", "status": "online", "category": "content"},
    {"name": "hermes-seo", "port": 8013, "model": "Gemini 2.0 Flash", "role": "SEO Specialist", "status": "online", "category": "content"},
    {"name": "hermes-funnel", "port": 8014, "model": "Claude Sonnet 4.6", "role": "Funnel Architect", "status": "online", "category": "revenue"},
    {"name": "hermes-etsy", "port": 8015, "model": "Claude Haiku 4.5", "role": "Etsy Manager", "status": "online", "category": "revenue"},
    {"name": "hermes-outreach", "port": 8016, "model": "Claude Sonnet 4.6", "role": "Outbound Sales", "status": "online", "category": "revenue"},
    {"name": "hermes-proposals", "port": 8017, "model": "Claude Sonnet 4.6", "role": "Proposal Writer", "status": "online", "category": "revenue"},
    {"name": "hermes-crm", "port": 8018, "model": "Claude Haiku 4.5", "role": "CRM Assistant", "status": "online", "category": "ops"},
    {"name": "hermes-crediversity", "port": 8019, "model": "Claude Sonnet 4.6", "role": "LMS Builder", "status": "online", "category": "education"},
    {"name": "hermes-hireed", "port": 8020, "model": "Claude Sonnet 4.6", "role": "WIL Coordinator", "status": "online", "category": "education"},
    {"name": "hermes-educonnect", "port": 8021, "model": "Claude Sonnet 4.6", "role": "Platform Ops", "status": "online", "category": "education"},
    {"name": "hermes-whop", "port": 8022, "model": "Claude Haiku 4.5", "role": "Membership Ops", "status": "online", "category": "revenue"},
    {"name": "hermes-tiktok", "port": 8023, "model": "Gemini 2.0 Flash", "role": "TikTok Creator", "status": "online", "category": "content"},
    {"name": "hermes-campaign", "port": 8024, "model": "Claude Sonnet 4.6", "role": "Campaign Manager", "status": "online", "category": "content"},
    {"name": "hermes-gumroad", "port": 8025, "model": "Claude Haiku 4.5", "role": "Product Sales", "status": "online", "category": "revenue"},
    {"name": "hermes-pinterest", "port": 8027, "model": "Gemini 2.0 Flash", "role": "Pinterest SEO", "status": "online", "category": "content"},
]

# ── Mock Data ─────────────────────────────────────────

LEADS = [
    {"id": "1", "name": "Sarah Chen", "email": "sarah.c@uoft.ca", "source": "TikTok", "status": "warm", "tags": ["OSAP", "AI-curious"], "created_at": "2026-06-15T09:23:00Z"},
    {"id": "2", "name": "Marcus Williams", "email": "m.williams@ryerson.ca", "source": "LinkedIn", "status": "hot", "tags": ["coaching", "career-change"], "created_at": "2026-06-14T14:11:00Z"},
    {"id": "3", "name": "Priya Patel", "email": "priya.p@mcmaster.ca", "source": "Whop", "status": "member", "tags": ["premium", "content-creator"], "created_at": "2026-06-12T08:45:00Z"},
    {"id": "4", "name": "James Okafor", "email": "j.okafor@yorku.ca", "source": "Discord", "status": "new", "tags": ["BSWD", "first-gen"], "created_at": "2026-06-16T22:30:00Z"},
    {"id": "5", "name": "Emily Tran", "email": "etran@uwaterloo.ca", "source": "Referral", "status": "warm", "tags": ["dev", "WIL-interest"], "created_at": "2026-06-13T11:05:00Z"},
    {"id": "6", "name": "David Kim", "email": "d.kim@ubc.ca", "source": "Instagram", "status": "new", "tags": ["AI-tools", "side-hustle"], "created_at": "2026-06-17T06:12:00Z"},
    {"id": "7", "name": "Aisha Mohammed", "email": "aisha.m@uottawa.ca", "source": "TikTok", "status": "hot", "tags": ["micro-cred", "resume-help"], "created_at": "2026-06-16T15:48:00Z"},
    {"id": "8", "name": "Liam O'Brien", "email": "liam.ob@dal.ca", "source": "Email Campaign", "status": "warm", "tags": ["freelance", "AI-services"], "created_at": "2026-06-11T19:22:00Z"},
]

HERMES_RESPONSES = {
    "default": """Based on your request, here's my strategic assessment:

**Key Insight:** The EdVisingU ecosystem is positioned at the intersection of AI automation and student income generation — a market with zero direct competitors in Canada.

**Immediate Actions:**
1. Push the Content Factory to generate 3 LinkedIn posts targeting OSAP-eligible students
2. Route to hermes-finance for this week's MRR update  
3. Schedule a deep-research task on competitor positioning via hermes-research

**Revenue Impact:** Each qualified lead from this content cycle has a $47/month LTV at current conversion rates. A batch of 5 posts historically generates 12-18 leads.

Want me to dispatch this to the content team or dig deeper on any of these points?""",

    "revenue": """**Revenue Intelligence Report — Week of June 17, 2026**

| Metric | This Week | Last Week | Δ |
|--------|-----------|-----------|---|
| MRR | $4,230 | $3,995 | +5.9% |
| New Members | 8 | 5 | +60% |
| Churn | 1 | 2 | -50% |
| Gumroad Sales | $847 | $612 | +38.4% |
| Etsy Revenue | $234 | $189 | +23.8% |

**Top Performer:** TikTok → Whop funnel converted at 4.2% this week (up from 2.8%).

**Alert:** 3 members are approaching 90-day mark without engagement. Recommend triggering re-engagement sequence via hermes-email.

**Projection:** At current growth rate, $5,000 MRR by end of July.""",

    "content": """**Content Pipeline Status**

✅ Published today:
- LinkedIn: "Why 90% of students leave $50K on the table" (1,247 impressions, 89 engagements)
- TikTok: "OSAP hack nobody talks about" (12.4K views, 834 likes)

📋 In queue (pending Dr. D approval):
- Email newsletter: "The AI Side Hustle Blueprint" — scheduled for Thursday 8am
- YouTube Short: "I built a 25-agent AI system for $30/month"
- Instagram carousel: "5 AI tools replacing entry-level jobs (and how to be the one using them)"

🔄 Generating now:
- Dispatching to hermes-tiktok for trending audio match
- hermes-seo running keyword analysis on "Canadian student AI tools"

Want me to approve the queue or regenerate any of these?""",
}

CONTENT_SAMPLES = {
    "linkedin": """🚀 I built a 25-agent AI system that runs my entire business.

Cost? $30/month on a Hetzner VPS.

Here's what it does while I sleep:
→ Generates content for 5 platforms
→ Scores resumes and coaches users
→ Tracks revenue and flags anomalies
→ Manages 200+ community members

The tech stack:
• Claude Sonnet 4.6 for strategy
• GPT-4o for code generation
• Gemini Flash for web research
• Local Ollama for zero-cost tasks

Most people don't realize how accessible this is now.

The gap isn't talent. It's systems.

I built the system. Now I'm teaching others how to do it too.

DM me "AI" if you want the blueprint.

#AI #Automation #BuildInPublic""",

    "tiktok": """[HOOK - 0:00] "I replaced a 6-person team with 25 AI agents for $30 a month."

[BUILD - 0:03] "Every morning at 7am, my system sends me a revenue report, flags any issues, and has already written 3 pieces of content for me."

[VALUE - 0:12] "One agent handles my TikTok scripts. Another manages my email list. Another scores resumes for people who need career help."

[PROOF - 0:22] "Last month this system generated $4,200 in recurring revenue — while I was focused on building."

[CTA - 0:32] "I'm giving away the exact blueprint. Link in bio."

[END - 0:38]

🎵 Suggested audio: trending "tech bro" or "day in my life" sound
📊 Target: 60-90 sec, vertical, face-to-camera with screen recordings""",

    "email": """Subject: The $30/month AI system running my entire business

Preview: 25 agents. Zero employees. Full autopilot.

---

Hey [First Name],

I want to show you something I built.

It's a system of 25 AI agents that runs on a single $30/month server. Each agent has a specific job:

- **Hermes Core** → Executive assistant (daily briefings, strategic planning)
- **Content Factory** → Writes for LinkedIn, TikTok, YouTube, and email automatically
- **Research Agent** → Deep research and market intelligence on demand
- **Finance Agent** → Tracks MRR, flags churn, projects revenue
- **Builder Agent** → Scaffolds new projects and writes code

The whole system was built following a blueprint I'm now sharing.

**Here's what you need to know:**

You don't need to be a developer to build this. You need a blueprint, a VPS, and the willingness to follow the manual step by step.

→ [Get Access — Reply to this email]

This is the same system generating $4,000+/month for me right now.

— Hamza

---
Unsubscribe | Manage preferences""",
}

# ── Endpoints ─────────────────────────────────────────

@app.get("/health")
def health():
    return {
        "status": "operational",
        "version": "2.0.0",
        "system": "AI Command Center",
        "owner": "Hamza Paracha",
        "uptime": "14d 6h 23m",
        "agents_online": 25,
        "agents_total": 25,
        "last_health_check": datetime.now().isoformat(),
    }

@app.get("/agents")
def list_agents():
    return {"agents": FLEET, "total": len(FLEET), "online": 25}

@app.get("/agents/{agent_name}")
def get_agent(agent_name: str):
    agent = next((a for a in FLEET if a["name"] == agent_name), None)
    if not agent:
        return {"error": "Agent not found"}
    return {
        **agent,
        "uptime": f"{random.randint(10,14)}d {random.randint(0,23)}h",
        "requests_today": random.randint(45, 320),
        "avg_response_ms": random.randint(180, 2400),
        "memory_mb": random.randint(280, 520),
    }

@app.get("/leads")
def get_leads():
    return {"leads": LEADS, "total": len(LEADS), "new": 2, "hot": 2, "warm": 3}

@app.get("/stats")
def get_stats():
    return {
        "mrr": 4230,
        "mrr_change": 5.9,
        "members": 89,
        "leads_total": len(LEADS),
        "leads_this_week": 4,
        "content_published_today": 2,
        "content_in_queue": 3,
        "agents_online": 25,
        "uptime_percent": 99.7,
    }

@app.post("/chat")
async def chat(req: ChatRequest):
    await asyncio.sleep(random.uniform(0.5, 1.5))  # Simulate thinking
    msg_lower = req.message.lower()
    if any(w in msg_lower for w in ["revenue", "mrr", "money", "income", "sales"]):
        response = HERMES_RESPONSES["revenue"]
    elif any(w in msg_lower for w in ["content", "post", "write", "publish", "tiktok"]):
        response = HERMES_RESPONSES["content"]
    else:
        response = HERMES_RESPONSES["default"]
    return {
        "response": response,
        "agent": req.agent,
        "model": "Claude Sonnet 4.6",
        "tokens_used": random.randint(800, 2200),
        "latency_ms": random.randint(1200, 3400),
        "memory_context": "5 relevant documents retrieved from ChromaDB",
        "timestamp": datetime.now().isoformat(),
    }

@app.post("/content/generate")
async def generate_content(req: ContentRequest):
    await asyncio.sleep(random.uniform(1.0, 2.0))  # Simulate generation
    content = {}
    for platform in req.platforms:
        if platform in CONTENT_SAMPLES:
            content[platform] = CONTENT_SAMPLES[platform].replace("[TOPIC]", req.topic)
        else:
            content[platform] = f"Generated {platform} content for: {req.topic}"
        store.insert_content(req.topic, platform, raw_content=content[platform], status="pending")
    return {
        "topic": req.topic,
        "content": content,
        "model": "Claude Sonnet 4.6",
        "tokens_used": random.randint(2000, 4500),
        "generation_time_ms": random.randint(3200, 6800),
        "platforms_generated": len(content),
    }

@app.post("/hermes/chat")
async def hermes_chat(req: ChatRequest):
    return await chat(req)

@app.post("/advisor/chat")
async def advisor_chat(req: ChatRequest):
    await asyncio.sleep(random.uniform(0.5, 1.2))
    return {
        "response": f"""Great question! Based on what you're asking about, here's my recommendation:

**For Canadian students looking to earn while studying:**

1. **OSAP + BSWD Optimization** — Most students leave $2,000-$8,000 on the table. I can walk you through the application strategy.

2. **AI Side Hustle Path** — Start with the EdVisingU membership ($47/mo). You'll learn to build AI tools that businesses will pay $500-2,000/month for.

3. **Work-Integrated Learning** — HireEd Nexus Labs (gohireed.com) has 3 active projects matching your profile right now.

**Next step:** Would you like me to run a skills assessment, or should I pull up the current WIL opportunities?""",
        "agent": "hermes-advisor",
        "model": "Claude Sonnet 4.6",
    }

@app.post("/credihire/analyze")
async def analyze_resume(req: ResumeRequest):
    await asyncio.sleep(random.uniform(0.8, 1.5))
    return {
        "ats_score": 72,
        "overall_grade": "B-",
        "strengths": [
            "Clear chronological format",
            "Quantified achievements in 3/5 roles",
            "Strong action verbs in bullet points",
        ],
        "weaknesses": [
            "Missing 6 critical keywords for target role",
            "Summary section is generic — not tailored to job posting",
            "No skills section — ATS systems will miss technical competencies",
        ],
        "improvements": [
            "Add a dedicated 'Technical Skills' section with exact keywords from job posting",
            "Rewrite summary to mirror the language of the target role",
            "Add metrics to the 2 roles missing quantified results",
            "Include 'Projects' section for portfolio-worthy work",
        ],
        "keyword_gaps": ["Python", "data analysis", "stakeholder management", "agile", "project coordination", "KPI reporting"],
    }

@app.get("/v1/models")
def list_models():
    return {"data": [{"id": a["name"], "object": "model", "owned_by": "edvisingu"} for a in FLEET]}

# ── CrediHire: optimize / cover-letter / LinkedIn (Manual 10.2) ──

@app.post("/credihire/optimize")
async def optimize_resume(req: ResumeRequest):
    await asyncio.sleep(random.uniform(0.6, 1.2))
    return {
        "optimized_resume": (
            "PROFESSIONAL SUMMARY\nResults-driven professional aligned to the target role, "
            "with quantified impact and ATS-optimized keywords woven throughout.\n\n"
            "TECHNICAL SKILLS\nPython | Data Analysis | Stakeholder Management | Agile | KPI Reporting\n\n"
            "EXPERIENCE\n- Rewrote bullet points to lead with action verbs and measurable outcomes.\n"
            "- Mirrored the language of the job description to pass ATS keyword filters."
        ),
        "ats_score_after": 91,
        "ats_score_before": 72,
        "model": "Claude Sonnet 4.6",
    }

@app.post("/credihire/cover-letter")
async def cover_letter(req: ResumeRequest):
    await asyncio.sleep(random.uniform(0.6, 1.2))
    return {
        "cover_letter": (
            "Dear Hiring Manager,\n\nI'm writing to express my strong interest in this role. "
            "My background maps directly to your requirements, and I've delivered measurable results "
            "in every position I've held.\n\nI'd welcome the opportunity to discuss how I can contribute.\n\n"
            "Sincerely,\n[Candidate Name]"
        ),
        "model": "Claude Sonnet 4.6",
    }

@app.post("/credihire/linkedin-summary")
async def linkedin_summary(req: ResumeRequest):
    await asyncio.sleep(random.uniform(0.4, 1.0))
    return {
        "linkedin_summary": (
            "I help organizations turn ambiguity into shipped outcomes. Over my career I've combined "
            "technical depth with clear communication to drive measurable impact. Currently focused on "
            "AI-assisted productivity and building systems that scale. Open to opportunities where I can "
            "create outsized value."
        ),
        "model": "Claude Sonnet 4.6",
    }

# ── Content tools: HeyGen + ElevenLabs (mock) (Manual 12.1/12.2) ──

@app.post("/heygen/generate")
async def heygen_generate(req: HeyGenRequest):
    await asyncio.sleep(random.uniform(0.5, 1.0))
    return {
        "mock": True,
        "video_id": f"mock_vid_{abs(hash(req.script)) % 100000}",
        "status": "processing",
        "avatar_id": req.avatar_id,
        "estimated_seconds": random.randint(40, 120),
        "note": "Mock HeyGen job. Set HEYGEN_API_KEY + ARCH_BACKEND=live for real video.",
    }

@app.post("/elevenlabs/speak")
async def elevenlabs_speak(req: TTSRequest):
    await asyncio.sleep(random.uniform(0.3, 0.8))
    return {
        "mock": True,
        "audio_path": f"/tmp/mock_audio_{abs(hash(req.text)) % 100000}.mp3",
        "voice_id": req.voice_id,
        "duration_sec": round(len(req.text) / 14.0, 1),
        "note": "Mock ElevenLabs output. Set ELEVENLABS_API_KEY + ARCH_BACKEND=live for real audio.",
    }

# ── Whop membership webhook -> local store (Manual 12.4) ──

@app.post("/whop/webhook")
async def whop_webhook(evt: WhopEvent):
    if evt.event == "member.created":
        result = store.upsert_member(evt.email, name=evt.name, whop_id=evt.whop_id, plan=evt.plan)
        action = "member added + welcome email queued (mock)"
    elif evt.event == "member.deleted":
        result = store.deactivate_member(evt.email)
        action = "member cancelled"
    else:
        result = {"ignored": evt.event}
        action = "no-op"
    return {"event": evt.event, "result": result, "action": action}

@app.get("/members")
def members():
    rows = store.list_members()
    return {"members": rows, "total": len(rows), "active": sum(1 for m in rows if m["status"] == "active")}

@app.get("/content")
def content_queue(status: str | None = None):
    rows = store.list_content(status=status)
    return {"content": rows, "total": len(rows)}

# ── Agent Task Bus demo (Manual 20.6 / 24.7) ──

@app.post("/taskbus/demo")
async def taskbus_demo(req: ChatRequest):
    task_id = f"task-{int(time.time())}-{random.randint(100, 999)}"
    return {
        "task_id": task_id,
        "flow": [
            {"stage": "inbox", "agent": "hermes-core", "action": "decomposed request into 1 subtask"},
            {"stage": "working", "agent": req.agent, "action": f"processing: {req.message[:60]}"},
            {"stage": "outbox", "agent": req.agent, "result": "subtask complete, result returned to orchestrator"},
        ],
        "status": "completed",
        "note": "File-based queue at data/agent-bus/{inbox,working,outbox}. Redis path behind ARCH_BACKEND=live.",
    }

# ── Multi-model routing summary (Manual Section 26) ──

ROUTING = {
    "claude-sonnet-4-6": ["hermes-core", "hermes-content", "hermes-advisor", "hermes-credihire",
                            "hermes-research", "hermes-email", "hermes-proposals", "hermes-outreach",
                            "hermes-crediversity", "hermes-hireed", "hermes-educonnect", "hermes-funnel",
                            "hermes-campaign"],
    "claude-haiku-4-5": ["hermes-ops", "hermes-finance", "hermes-crm", "hermes-whop", "hermes-etsy", "hermes-gumroad"],
    "gemini-2.0-flash": ["hermes-social", "hermes-seo", "hermes-tiktok", "hermes-ads", "hermes-pinterest"],
    "gpt-4o": ["hermes-builder"],
}

@app.get("/routing")
def routing():
    return {
        "models": {m: {"agents": a, "count": len(a)} for m, a in ROUTING.items()},
        "total_agents": sum(len(a) for a in ROUTING.values()),
        "note": "Right model for every agent (Manual Section 26). Mock mode labels the route; live mode calls it.",
    }

# ── Monitoring / health rollup (Manual Section 25) ──

@app.get("/monitoring")
def monitoring():
    services = [
        {"name": "fastapi-router", "port": 8000, "status": "up", "latency_ms": random.randint(2, 20)},
        {"name": "n8n", "port": 5678, "status": "up", "latency_ms": random.randint(5, 40)},
        {"name": "open-webui", "port": 3000, "status": "up", "latency_ms": random.randint(5, 30)},
        {"name": "redis", "port": 6379, "status": "up", "latency_ms": random.randint(1, 5)},
        {"name": "chromadb", "port": 8800, "status": "up", "latency_ms": random.randint(3, 25)},
    ] + [
        {"name": a["name"], "port": a["port"], "status": "up", "latency_ms": random.randint(10, 60)}
        for a in FLEET
    ]
    up = sum(1 for s in services if s["status"] == "up")
    return {
        "services": services,
        "total": len(services),
        "up": up,
        "down": len(services) - up,
        "uptime_percent": 99.7,
        "checked_at": datetime.now().isoformat(),
    }

# ── DrDDurham political campaign automation (Manual Section 30) ──

# Canada Elections Act / Ontario Municipal Elections Act authorization line that
# MUST appear on all paid/published campaign content (Manual 30.4).
CAMPAIGN_AUTHORIZATION = "Authorized by the Official Agent for DrDDurham."

CAMPAIGN_BRAND = {
    "name": "DrDDurham",
    "handle": "@DrDDurham",
    "slogan": "Built to Lead. Ready for Pickering.",
    "colors": {"navy": "#1B3A5C", "gold": "#D4A843", "white": "#FFFFFF"},
    "email": "campaign@drddurham.ca",
    "website": "drddurham.ca",
    "election_date": "2026-10-26",
    "riding": "Pickering, Ontario",
    "primary_platform": "Facebook Page @DrDDurham",
    "secondary_platforms": ["Instagram", "TikTok", "X", "YouTube"],
}

CAMPAIGN_COMPLIANCE = [
    'All paid ads include: "Authorized by [Campaign Agent Name], [Campaign Name]"',
    "Track all campaign expenses (incl. AI tool costs) in a separate spreadsheet — required by law",
    "No vote-buying, voter suppression, or misleading statements about voting procedures",
    "Check Elections Ontario (elections.on.ca) for exact ad blackout periods before scheduling",
    "AI content assistance is legal under current Canadian law (May 2026); stay updated",
]


def _campaign_facebook_posts(theme: str) -> list[dict]:
    angles = [
        "Why Pickering's future runs on education and technology",
        "Meet Dr. D: from classroom to community leadership",
        "3 ideas to make Pickering work for working families",
        "Local jobs, local skills: a plan for Durham Region",
        "Town hall recap — what residents told us this week",
        "Volunteer spotlight: the people powering this campaign",
        "Get out and vote: October 26 — here's how and where",
    ]
    return [
        {
            "platform": "facebook",
            "post": f"{angle}.\n\n{CAMPAIGN_BRAND['slogan']}\n\n{CAMPAIGN_AUTHORIZATION}",
            "authorization": CAMPAIGN_AUTHORIZATION,
        }
        for angle in angles
    ]


def _campaign_tiktok_scripts(theme: str) -> list[dict]:
    hooks = [
        "The one thing Pickering council keeps getting wrong",
        "I'm a doctor of education running for office — here's why",
        "60 seconds on how we fund local skills training",
        "What young families in Pickering actually need",
        "How to vote on October 26 (it takes 5 minutes)",
    ]
    return [
        {
            "platform": "tiktok",
            "script": f"[HOOK 0:00] {hook}\n[BODY 0:05] Short, plain-language explanation.\n"
                      f"[CTA 0:25] {CAMPAIGN_BRAND['slogan']} Follow {CAMPAIGN_BRAND['handle']}.\n"
                      f"[DISCLOSURE] {CAMPAIGN_AUTHORIZATION}",
            "authorization": CAMPAIGN_AUTHORIZATION,
        }
        for hook in hooks
    ]


def _campaign_instagram_carousels(theme: str) -> list[dict]:
    topics = [
        "3-point plan for Pickering",
        "Where Dr. D stands on local issues",
        "How to vote: dates, locations, ID",
    ]
    return [
        {
            "platform": "instagram",
            "carousel": [f"Slide 1: {topic}", "Slide 2: The problem", "Slide 3: The plan",
                         f"Slide 4: {CAMPAIGN_BRAND['slogan']}", f"Slide 5: {CAMPAIGN_AUTHORIZATION}"],
            "authorization": CAMPAIGN_AUTHORIZATION,
        }
        for topic in topics
    ]


def _campaign_email_drafts(theme: str) -> list[dict]:
    return [
        {
            "platform": "email",
            "subject": "Built to Lead. Ready for Pickering.",
            "body": "Friends,\n\nThis week we knocked on doors across the ward...\n\n"
                    f"{CAMPAIGN_AUTHORIZATION}",
            "review": "Draft only — Lahari QA + Dr. D approval required before send.",
        },
        {
            "platform": "email",
            "subject": "October 26: your vote, your Pickering",
            "body": "It's almost time...\n\nHere's how and where to vote.\n\n"
                    f"{CAMPAIGN_AUTHORIZATION}",
            "review": "Draft only — Lahari QA + Dr. D approval required before send.",
        },
    ]


@app.get("/campaign/brand")
def campaign_brand():
    """DrDDurham brand + platform specs and electoral compliance rules (Manual 30.1/30.4)."""
    return {"brand": CAMPAIGN_BRAND, "compliance": CAMPAIGN_COMPLIANCE,
            "authorization_line": CAMPAIGN_AUTHORIZATION}


@app.post("/campaign/generate")
async def campaign_generate(req: CampaignRequest):
    """Weekly campaign content automation (Manual 30.3).

    Generates the manual's exact weekly batch — 7 Facebook posts, 5 TikTok
    scripts, 3 Instagram carousels, 2 email drafts — each carrying the required
    Canada Elections Act authorization line. Drafts persist to the local store
    pending Dr. D's Telegram approval before Blotato scheduling.
    """
    await asyncio.sleep(random.uniform(0.8, 1.6))
    facebook = _campaign_facebook_posts(req.theme)
    tiktok = _campaign_tiktok_scripts(req.theme)
    instagram = _campaign_instagram_carousels(req.theme)
    emails = _campaign_email_drafts(req.theme)

    saved = []
    for item in facebook + tiktok + instagram:
        row = store.insert_content(
            f"DrDDurham — {req.theme}", item["platform"],
            raw_content=str(item.get("post") or item.get("script") or item.get("carousel")),
            status="pending_campaign_approval",
        )
        saved.append(row["id"])

    return {
        "agent": "hermes-campaign",
        "model": "Claude Sonnet 4.6",
        "week_of": req.week_of or datetime.now().strftime("%Y-%m-%d"),
        "theme": req.theme,
        "content": {
            "facebook_posts": facebook,
            "tiktok_scripts": tiktok,
            "instagram_carousels": instagram,
            "email_drafts": emails,
        },
        "counts": {"facebook": len(facebook), "tiktok": len(tiktok),
                   "instagram": len(instagram), "email": len(emails)},
        "saved_to_drive": "drive.google.com/campaign (mock — review folder)",
        "status": "pending_approval",
        "approval_flow": "Dr. D reviews via Telegram: /approve-campaign or /revise [note]",
        "compliance": CAMPAIGN_COMPLIANCE,
        "authorization_line": CAMPAIGN_AUTHORIZATION,
        "saved_content_ids": saved,
    }


@app.post("/campaign/schedule")
async def campaign_schedule(req: CampaignScheduleRequest):
    """On Dr. D's approval, schedule posts via Blotato (Manual 30.3 step 112)."""
    from tools import blotato_tools

    when = req.scheduled_at or (datetime.now() + timedelta(days=1)).isoformat()
    result = await blotato_tools.schedule_post(
        content="DrDDurham approved weekly batch",
        platforms=["facebook", "instagram", "tiktok", "x"],
        scheduled_at=when,
    )
    return {
        "agent": "hermes-campaign",
        "scheduled": result,
        "post_ids": req.post_ids,
        "authorization_line": CAMPAIGN_AUTHORIZATION,
        "note": "Blotato multi-platform schedule (mock by default; live with BLOTATO_API_KEY).",
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
