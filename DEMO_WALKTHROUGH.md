# EdVisingU AI Ecosystem — Demo Walkthrough

## Quick Start (30 seconds)

```bash
bash ~/Downloads/edvisingu/demo.sh
```

Then open: **http://localhost:3000**

---

## Demo Script (5-7 minutes, designed to impress)

### 1. Command Center (30 sec)

Open **http://localhost:3000/dashboard**

**What they see:**
- $4,230 MRR with +5.9% growth
- 89 active members
- 25/25 agents online at 99.7% uptime
- Live activity feed showing recent agent actions
- Full system architecture with ports

**What to say:**
> "This is the command center. Everything you see here is live data from a 25-agent AI system that runs 24/7 on a $30/month VPS. Each agent is a specialist — content, finance, student advising, resume scoring — all running in Docker containers with different AI models assigned based on the task."

---

### 2. Hermes AI Chat (90 sec) — THE WOW MOMENT

Open **http://localhost:3000/dashboard/hermes**

**Demo flow:**
1. Click the suggested prompt: **"Show me this week's revenue"**
2. Watch the typing indicator animate
3. Revenue report appears with a formatted table, growth metrics, and strategic recommendations

**What to say:**
> "This is Hermes — my executive AI assistant. It has persistent memory via ChromaDB, so it remembers every conversation. Watch this."

4. Then type: **"What's in the content pipeline?"**
5. Get back a full pipeline status with published content, queue items, and active generation tasks

**What to say:**
> "In production, this routes through Claude Sonnet 4.6 with retrieval-augmented generation. It pulls context from previous conversations and ecosystem knowledge before responding."

**Point out** the metadata at the bottom of each response: model name, latency, token count.

---

### 3. Content Factory (60 sec)

Open **http://localhost:3000/dashboard/content**

**Demo flow:**
1. Type topic: **"How Canadian students can earn $500/month using AI tools"**
2. Keep all 3 platforms selected (LinkedIn, TikTok, Email)
3. Click "Generate Content"
4. Watch loading state, then full content appears for all 3 platforms

**What to say:**
> "One topic goes in. Three pieces of platform-optimized content come out. The LinkedIn post follows the 1200-char rule with a hook. The TikTok script is timestamped for filming. The email has subject line, preview text, and full body with CTA."

5. Click the **Copy** button on the LinkedIn post

> "In production, this flows into Blotato for auto-scheduling across all platforms. One click, all channels published."

---

### 4. Leads CRM (30 sec)

Open **http://localhost:3000/dashboard/leads**

**What they see:**
- 8 student leads from different Canadian universities
- Color-coded status: new (blue), warm (amber), hot (red), member (green)
- Source tracking: TikTok, LinkedIn, Discord, Referral, Whop
- Tags showing interests: OSAP, BSWD, AI-curious, coaching

**What to say:**
> "Every lead gets automatically captured when they engage with content or join Discord. The CRM tags them by interest and source so we know exactly which funnel they came through. Hot leads get automated outreach via hermes-email."

Try the **search bar** — type "uoft" to filter.

---

### 5. Agent Fleet (60 sec) — TECHNICAL DEPTH

Open **http://localhost:3000/dashboard/fleet**

**What they see:**
- All 25 agents in a grid with green status dots
- Model distribution breakdown: 14x Claude Sonnet, 6x Haiku, 4x Gemini, 1x GPT-4o
- Category filters: Core, Content, Education, Revenue, Ops, Dev

**Demo flow:**
1. Show the model distribution card at the top
2. Click "Revenue & Sales" filter — shows 6 revenue-focused agents
3. Click "Content & Marketing" — shows 7 content agents
4. Point out the port numbers (8001-8027)

**What to say:**
> "25 agents, 4 different AI models, all containerized in Docker. Claude Sonnet handles strategy and writing. Haiku handles fast cheap tasks. GPT-4o handles code generation. Gemini handles web research. Each agent has its own personality file — we call it SOUL.md — that defines its expertise, rules, and tone."

5. Point at the bottom stats: **25 containers, 4 models, $30/month**

> "All of this runs on a single Hetzner VPS for thirty dollars a month."

---

### 6. API Swagger (optional, 30 sec)

Open **http://localhost:8000/docs**

> "Every agent is accessible via REST API. This is the auto-generated Swagger documentation. You can test any endpoint live."

---

## Killshot Lines

- "This is an AI operating system, not a chatbot."
- "25 agents, 4 models, zero employees, $30/month infrastructure."
- "Every piece of content, every lead, every student interaction — automated."
- "The system works while we sleep."

---

## To Stop

Press **Ctrl+C** in the terminal running `demo.sh`.
