"use client";

import { useEffect, useState } from "react";
import { Cpu } from "lucide-react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface Agent { name: string; port: number; model: string; role: string; status: string; category: string; }

const MODEL_STYLE: Record<string, string> = {
  "Claude Sonnet 4.6": "border-violet-500/15 text-violet-400 bg-violet-500/5",
  "Claude Haiku 4.5": "border-sky-500/15 text-sky-400 bg-sky-500/5",
  "GPT-4o": "border-emerald-500/15 text-emerald-400 bg-emerald-500/5",
  "Gemini 2.0 Flash": "border-amber-500/15 text-amber-400 bg-amber-500/5",
};

const CATS: Record<string, string> = {
  core: "Core", content: "Content", education: "Education", revenue: "Revenue", ops: "Operations", dev: "Development",
};

export default function Fleet() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [cat, setCat] = useState("all");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API}/agents`).then((r) => r.json()).then((d) => { setAgents(d.agents); setLoading(false); }).catch(() => setLoading(false));
  }, []);

  const filtered = cat === "all" ? agents : agents.filter((a) => a.category === cat);
  const modelCounts = agents.reduce((acc, a) => { acc[a.model] = (acc[a.model] || 0) + 1; return acc; }, {} as Record<string, number>);

  if (loading) return <div className="flex h-64 items-center justify-center"><div className="h-5 w-5 animate-spin rounded-full border-2 border-[var(--accent)] border-t-transparent" /></div>;

  return (
    <div className="animate-in">
      <div className="flex items-end justify-between mb-5">
        <div>
          <h1 className="text-xl font-semibold tracking-tight">Agent Fleet</h1>
          <p className="text-[12px] text-[var(--text-muted)] mt-0.5">25 specialist agents · multi-model · containerized</p>
        </div>
        <div className="flex items-center gap-1.5 badge bg-[var(--success-dim)] border border-emerald-500/20 text-emerald-400">
          <span className="dot dot-live" />
          {agents.length}/{agents.length}
        </div>
      </div>

      {/* Models */}
      <div className="flex flex-wrap gap-2 mb-5">
        {Object.entries(modelCounts).map(([model, count]) => (
          <div key={model} className={`badge border gap-1.5 ${MODEL_STYLE[model] ?? ""}`}>
            <Cpu size={8} />
            <span>{model}</span>
            <span className="opacity-50">×{count}</span>
          </div>
        ))}
      </div>

      {/* Filters */}
      <div className="flex gap-1 mb-4 flex-wrap">
        {["all", ...Object.keys(CATS)].map((c) => (
          <button key={c} onClick={() => setCat(c)} className={`rounded-md px-2.5 py-1 text-[10px] font-medium transition-colors ${cat === c ? "bg-[var(--accent-dim)] text-[var(--accent)] border border-[var(--accent-border)]" : "text-[var(--text-muted)] hover:text-[var(--text-secondary)]"}`}>
            {c === "all" ? "All" : CATS[c]}
          </button>
        ))}
      </div>

      {/* Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
        {filtered.map((agent) => (
          <div key={agent.name} className="card px-3.5 py-3 flex flex-col gap-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="dot dot-live" />
                <span className="text-[12px] font-medium">{agent.name}</span>
              </div>
              <span className="font-mono text-[9px] text-[var(--text-muted)]">:{agent.port}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-[10px] text-[var(--text-muted)]">{agent.role}</span>
              <span className={`badge border text-[8px] ${MODEL_STYLE[agent.model] ?? ""}`}>{agent.model.split(" ").slice(-1)}</span>
            </div>
          </div>
        ))}
      </div>

      {/* Summary */}
      <div className="grid grid-cols-3 gap-2 mt-5">
        {[["25", "Containers"], ["4", "Models"], ["$30", "/mo infra"]].map(([v, l]) => (
          <div key={l} className="card py-3 text-center">
            <p className="text-lg font-semibold">{v}</p>
            <p className="text-[9px] uppercase tracking-[0.1em] text-[var(--text-muted)]">{l}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
