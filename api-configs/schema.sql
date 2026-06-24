-- EdVisingU AI Ecosystem - Supabase Schema
-- Run in Supabase SQL Editor (Database > SQL Editor)

-- Enable vector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- AI Memory table (Supabase-based vector search alternative to ChromaDB)
CREATE TABLE IF NOT EXISTS ai_memory (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    agent_name TEXT NOT NULL,
    content TEXT NOT NULL,
    embedding VECTOR(1536),
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Leads / Student CRM
CREATE TABLE IF NOT EXISTS leads (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT,
    email TEXT UNIQUE,
    source TEXT,
    status TEXT DEFAULT 'new',
    tags TEXT[],
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Content Pipeline Queue
CREATE TABLE IF NOT EXISTS content_queue (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    topic TEXT NOT NULL,
    platform TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    raw_content TEXT,
    final_content TEXT,
    scheduled_at TIMESTAMPTZ,
    published_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Products / Courses / Offers
CREATE TABLE IF NOT EXISTS products (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    price NUMERIC,
    description TEXT,
    platform TEXT,
    url TEXT,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Members / Subscribers
CREATE TABLE IF NOT EXISTS members (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    name TEXT,
    whop_id TEXT,
    plan TEXT,
    status TEXT DEFAULT 'active',
    joined_at TIMESTAMPTZ DEFAULT now()
);

-- Enable Row Level Security on all tables
ALTER TABLE ai_memory ENABLE ROW LEVEL SECURITY;
ALTER TABLE leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE content_queue ENABLE ROW LEVEL SECURITY;
ALTER TABLE products ENABLE ROW LEVEL SECURITY;
ALTER TABLE members ENABLE ROW LEVEL SECURITY;

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_ai_memory_agent ON ai_memory(agent_name);
CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);
CREATE INDEX IF NOT EXISTS idx_leads_email ON leads(email);
CREATE INDEX IF NOT EXISTS idx_content_queue_status ON content_queue(status);
CREATE INDEX IF NOT EXISTS idx_content_queue_platform ON content_queue(platform);
CREATE INDEX IF NOT EXISTS idx_members_status ON members(status);
CREATE INDEX IF NOT EXISTS idx_members_whop_id ON members(whop_id);

-- Storage buckets (create these manually in Supabase Dashboard > Storage):
-- brand-assets (Public: YES) - Logos, brand images, social media assets
-- course-content (Public: NO) - Course videos, PDFs, lesson materials
-- resumes (Public: NO) - CrediHire resume uploads
-- avatars (Public: YES) - HeyGen AI avatar output files
-- audio (Public: YES) - ElevenLabs voice output files
