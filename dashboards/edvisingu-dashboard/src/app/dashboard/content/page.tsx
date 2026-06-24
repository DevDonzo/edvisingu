"use client";

import { useState } from "react";
import { Sparkles, Loader2, Copy, Check, Linkedin, Video, Mail } from "lucide-react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const PLATFORMS: Record<string, { icon: React.ElementType; label: string }> = {
  linkedin: { icon: Linkedin, label: "LinkedIn" },
  tiktok: { icon: Video, label: "TikTok" },
  email: { icon: Mail, label: "Email" },
};

export default function ContentFactory() {
  const [topic, setTopic] = useState("");
  const [platforms, setPlatforms] = useState(["linkedin", "tiktok", "email"]);
  const [content, setContent] = useState<Record<string, string> | null>(null);
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState<string | null>(null);
  const [meta, setMeta] = useState<{ tokens?: number; time?: number } | null>(null);

  const generate = async () => {
    if (!topic.trim() || loading) return;
    setLoading(true); setContent(null);
    try {
      const res = await fetch(`${API}/content/generate`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ topic, platforms }) });
      const data = await res.json();
      setContent(data.content);
      setMeta({ tokens: data.tokens_used, time: data.generation_time_ms });
    } catch { setContent(null); }
    setLoading(false);
  };

  const copy = (key: string, text: string) => { navigator.clipboard.writeText(text); setCopied(key); setTimeout(() => setCopied(null), 2000); };
  const toggle = (p: string) => setPlatforms((prev) => prev.includes(p) ? prev.filter((x) => x !== p) : [...prev, p]);

  return (
    <div className="animate-in">
      <div className="mb-6">
        <h1 className="text-xl font-semibold tracking-tight">Content Factory</h1>
        <p className="text-[12px] text-[var(--text-muted)] mt-0.5">Topic in → multi-platform content out</p>
      </div>

      <div className="card p-5">
        <label className="text-[10px] font-medium uppercase tracking-[0.12em] text-[var(--text-muted)]">Topic</label>
        <input
          value={topic} onChange={(e) => setTopic(e.target.value)} onKeyDown={(e) => e.key === "Enter" && generate()}
          placeholder="e.g. How to earn $500/month with AI tools"
          className="input-field mt-2"
        />

        <div className="flex items-center gap-2 mt-3">
          {Object.entries(PLATFORMS).map(([key, { label }]) => (
            <button key={key} onClick={() => toggle(key)} className={`badge border transition-colors ${platforms.includes(key) ? "border-[var(--accent-border)] bg-[var(--accent-dim)] text-[var(--accent)]" : "border-[var(--border-subtle)] text-[var(--text-muted)] hover:text-[var(--text-secondary)]"}`}>
              {label}
            </button>
          ))}
        </div>

        <button onClick={generate} disabled={loading || !topic.trim()} className="btn-accent mt-4 disabled:opacity-30">
          {loading ? <Loader2 size={13} className="animate-spin" /> : <Sparkles size={13} />}
          {loading ? "Generating..." : "Generate"}
        </button>
      </div>

      {content && (
        <div className="mt-5 space-y-3 animate-up">
          {meta && (
            <div className="flex items-center gap-4 font-mono text-[10px] text-[var(--text-muted)]">
              <span>{(meta.time! / 1000).toFixed(1)}s</span>
              <span>{meta.tokens} tokens</span>
              <span>Claude Sonnet 4.6</span>
            </div>
          )}
          {Object.entries(content).map(([platform, text]) => {
            const pm = PLATFORMS[platform];
            if (!pm) return null;
            const Icon = pm.icon;
            return (
              <div key={platform} className="card overflow-hidden">
                <div className="flex items-center justify-between px-4 py-2.5 border-b border-[var(--border-subtle)]">
                  <div className="flex items-center gap-2">
                    <Icon size={12} className="text-[var(--text-muted)]" />
                    <span className="text-[11px] font-medium">{pm.label}</span>
                  </div>
                  <button onClick={() => copy(platform, text)} className="flex items-center gap-1 text-[10px] text-[var(--text-muted)] hover:text-[var(--text-primary)] transition-colors">
                    {copied === platform ? <><Check size={9} className="text-emerald-400" /> Copied</> : <><Copy size={9} /> Copy</>}
                  </button>
                </div>
                <pre className="px-4 py-3.5 text-[12px] leading-[1.7] text-[var(--text-secondary)] whitespace-pre-wrap font-sans max-h-[260px] overflow-y-auto">{text}</pre>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
