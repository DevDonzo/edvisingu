"use client";

import { useEffect, useState } from "react";
import { TrendingUp, ArrowUpRight } from "lucide-react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface Stats {
  mrr: number; mrr_change: number; members: number; leads_total: number;
  leads_this_week: number; content_published_today: number; content_in_queue: number;
  agents_online: number; uptime_percent: number;
}

export default function Overview() {
  const [stats, setStats] = useState<Stats | null>(null);

  useEffect(() => {
    fetch(`${API}/stats`).then((r) => r.json()).then(setStats).catch(() => {});
  }, []);

  if (!stats) return <div className="flex h-64 items-center justify-center"><div className="h-5 w-5 animate-spin rounded-full border-2 border-[var(--accent)] border-t-transparent" /></div>;

  return (
    <div className="animate-in">
      <div className="mb-8">
        <h1 className="text-xl font-semibold tracking-tight">Overview</h1>
        <p className="text-[13px] text-[var(--text-muted)] mt-1">System performance and key metrics</p>
      </div>

      {/* Metrics */}
      <div className="grid grid-cols-4 gap-3">
        {[
          { label: "Revenue", value: `$${stats.mrr.toLocaleString()}`, sub: "MRR", change: `+${stats.mrr_change}%` },
          { label: "Members", value: String(stats.members), sub: "Active", change: "+12%" },
          { label: "Leads", value: String(stats.leads_total), sub: `${stats.leads_this_week} this week`, change: null },
          { label: "Fleet", value: `${stats.agents_online}/25`, sub: `${stats.uptime_percent}% uptime`, change: null },
        ].map((m) => (
          <div key={m.label} className="card px-4 py-4">
            <p className="text-[10px] font-medium uppercase tracking-[0.1em] text-[var(--text-muted)]">{m.label}</p>
            <div className="flex items-baseline gap-2 mt-2">
              <span className="text-2xl font-semibold tracking-tight">{m.value}</span>
              {m.change && (
                <span className="flex items-center gap-0.5 text-[10px] font-medium text-emerald-400">
                  <ArrowUpRight size={9} />{m.change}
                </span>
              )}
            </div>
            <p className="text-[11px] text-[var(--text-muted)] mt-1">{m.sub}</p>
          </div>
        ))}
      </div>

      {/* Two columns */}
      <div className="grid grid-cols-2 gap-3 mt-4">
        {/* Activity */}
        <div className="card p-5">
          <p className="text-[11px] font-medium uppercase tracking-[0.1em] text-[var(--text-muted)] mb-4">Recent Activity</p>
          <div className="space-y-2.5">
            {[
              { agent: "hermes-content", action: "Published LinkedIn post", t: "2m" },
              { agent: "hermes-finance", action: "MRR report generated", t: "14m" },
              { agent: "hermes-tiktok", action: "Script drafted", t: "23m" },
              { agent: "hermes-advisor", action: "Student query handled", t: "31m" },
              { agent: "hermes-ops", action: "Health check passed", t: "45m" },
              { agent: "hermes-email", action: "Outreach draft ready", t: "52m" },
            ].map((item, i) => (
              <div key={i} className="flex items-center gap-3 group">
                <span className="dot dot-live opacity-60" />
                <div className="flex-1 min-w-0">
                  <p className="text-[12px] text-[var(--text-primary)] truncate">{item.action}</p>
                </div>
                <span className="font-mono text-[10px] text-[var(--text-muted)]">{item.agent}</span>
                <span className="text-[10px] text-[var(--text-muted)] w-8 text-right">{item.t}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Architecture */}
        <div className="card p-5">
          <p className="text-[11px] font-medium uppercase tracking-[0.1em] text-[var(--text-muted)] mb-4">Infrastructure</p>
          <div className="space-y-2">
            {[
              { name: "FastAPI Router", port: "8000" },
              { name: "Agent Fleet (25x Docker)", port: "8001–8027" },
              { name: "ChromaDB Memory", port: "8800" },
              { name: "Redis Task Bus", port: "6379" },
              { name: "n8n Automation", port: "5678" },
              { name: "Open WebUI", port: "3000" },
              { name: "Uptime Kuma", port: "3001" },
            ].map((s, i) => (
              <div key={i} className="flex items-center justify-between py-1">
                <div className="flex items-center gap-2.5">
                  <span className="dot dot-live" />
                  <span className="text-[12px]">{s.name}</span>
                </div>
                <span className="font-mono text-[10px] text-[var(--text-muted)]">:{s.port}</span>
              </div>
            ))}
          </div>
          <div className="mt-4 rounded-lg bg-[var(--accent-dim)] border border-[var(--accent-border)] px-3.5 py-2.5">
            <p className="text-[10px] font-medium text-[var(--accent)]">Multi-Model Routing</p>
            <p className="text-[10px] text-[var(--text-muted)] mt-0.5">Claude Sonnet · Haiku · GPT-4o · Gemini Flash</p>
          </div>
        </div>
      </div>
    </div>
  );
}
