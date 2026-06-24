from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
import os

knowledge = [
    "EdVisingU is an AI-powered education platform at edvisingu.com that teaches students how to earn income while studying.",
    "CrediVersity at crediversity.com offers AI micro-credentials and digital learning pathways for career transformation.",
    "DrD Learn is the course and digital product platform for Dr. Andre De Freitas.",
    "HireEd Nexus Labs at gohireed.com connects students to real work-integrated learning projects and income pathways.",
    "ai.edvisingu.com is the AI assistant hub for the EdVisingU ecosystem.",
    "Primary revenue streams: $47/month memberships on Whop, course sales on Skillplate.com and Gumroad, Etsy digital products, high-ticket coaching at $999+, AI consulting services, and SaaS products.",
    "Monetization platforms: Skillplate.com (owned storefront), Whop (memberships + community), Gumroad (digital downloads), Etsy (marketplace - semi-manual), Discord (community + Whop-gated access), Vercel (web apps).",
    "Content channels: TikTok, LinkedIn, YouTube Shorts, Instagram Reels, email newsletter.",
    "Tech stack: Next.js, Supabase, Vercel, n8n, Cloudflare, Ollama, Claude API, OpenRouter, FastAPI.",
    "OSAP and BSWD are Canadian student funding programs that are part of the ecosystem's automation focus.",
    "The student developer builds the AI infrastructure remotely - Dr. D is the founder and strategic lead.",
    "The AI ecosystem runs on a Hetzner CPX41 VPS with 8 vCPU, 16GB RAM, 240GB NVMe SSD.",
    "OpenJarvis is the top-level AI OS orchestrator that sits above the entire stack.",
    "hermes-agent (NousResearch) is the gateway layer handling Telegram, Discord, Slack, and WhatsApp.",
    "The 25-agent Docker fleet handles specialist processing via FastAPI router.",
    "Blotato handles AI-native social media scheduling, repurposing, and multi-platform publishing.",
]

db_path = os.path.join(os.path.dirname(__file__), "../../vector-db/chroma-data")
embeddings = OllamaEmbeddings(model="nomic-embed-text")
vectorstore = Chroma(
    persist_directory=db_path,
    embedding_function=embeddings,
    collection_name="hermes_memory",
)
ids = [f"seed_{i}" for i in range(len(knowledge))]
vectorstore.add_texts(texts=knowledge, ids=ids)
print(f"Knowledge seeded: {len(knowledge)} documents added to Hermes memory.")
