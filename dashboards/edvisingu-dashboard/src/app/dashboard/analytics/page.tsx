"use client";

import { useEffect, useState } from "react";
import {
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, Tooltip, ResponsiveContainer,
} from "recharts";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const REVENUE_BY_STREAM = [
  { name: "Whop", value: 4230 },
  { name: "Gumroad", value: 847 },
  { name: "Etsy", value: 234 },
  { name: "Coaching", value: 999 },
];

const MEMBER_GROWTH = [
  { week: "W1", members: 62 }, { week: "W2", members: 68 }, { week: "W3", members: 74 },
  { week: "W4", members: 81 }, { week: "W5", members: 84 }, { week: "W6", members: 89 },
];

const MODEL_MIX = [
  { name: "Sonnet 4.6", value: 13 },
  { name: "Haiku 4.5", value: 6 },
  { name: "Gemini Flash", value: 5 },
  { name: "GPT-4o", value: 1 },
];

const COLORS = ["#6366f1", "#22c55e", "#f59e0b", "#ef4444"];

export default function Analytics() {
  const [stats, setStats] = useState<any>(null);

  useEffect(() => {
    fetch(`${API}/stats`).then((r) => r.json()).then(setStats).catch(() => {});
  }, []);

  return (
    <div className="animate-in">
      <div className="mb-5">
        <h1 className="text-xl font-semibold tracking-tight">Analytics</h1>
        <p className="text-[12px] text-[var(--text-muted)] mt-0.5">Revenue, members & content performance</p>
      </div>

      <div className="grid grid-cols-4 gap-3 mb-5">
        <Kpi label="MRR" value={stats ? `$${stats.mrr.toLocaleString()}` : "—"} sub={stats ? `+${stats.mrr_change ?? 5.9}%` : ""} />
        <Kpi label="Members" value={stats ? stats.members : "—"} sub="active" />
        <Kpi label="Leads" value={stats ? stats.leads_total : "—"} sub="total" />
        <Kpi label="Uptime" value={stats ? `${stats.uptime_percent}%` : "—"} sub="30d" />
      </div>

      <div className="grid grid-cols-2 gap-5">
        <Panel title="Revenue by Stream ($/mo)">
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={REVENUE_BY_STREAM}>
              <XAxis dataKey="name" tick={{ fill: "#8b8b94", fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: "#8b8b94", fontSize: 11 }} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={{ background: "#15151a", border: "1px solid #2a2a32", borderRadius: 8, fontSize: 12 }} />
              <Bar dataKey="value" fill="#6366f1" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </Panel>

        <Panel title="Member Growth">
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={MEMBER_GROWTH}>
              <XAxis dataKey="week" tick={{ fill: "#8b8b94", fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: "#8b8b94", fontSize: 11 }} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={{ background: "#15151a", border: "1px solid #2a2a32", borderRadius: 8, fontSize: 12 }} />
              <Line type="monotone" dataKey="members" stroke="#22c55e" strokeWidth={2} dot={{ r: 3 }} />
            </LineChart>
          </ResponsiveContainer>
        </Panel>

        <Panel title="Model Distribution (25 agents)">
          <ResponsiveContainer width="100%" height={220}>
            <PieChart>
              <Pie data={MODEL_MIX} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={75} label={{ fill: "#8b8b94", fontSize: 10 }}>
                {MODEL_MIX.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
              </Pie>
              <Tooltip contentStyle={{ background: "#15151a", border: "1px solid #2a2a32", borderRadius: 8, fontSize: 12 }} />
            </PieChart>
          </ResponsiveContainer>
        </Panel>

        <Panel title="Content Pipeline">
          <div className="flex h-[220px] flex-col justify-center gap-4">
            <Stat label="Published" value={stats ? stats.content_published ?? 12 : "—"} />
            <Stat label="In Queue" value={stats ? stats.content_in_queue ?? 3 : "—"} />
            <Stat label="Total" value={stats ? stats.content_total ?? 15 : "—"} />
          </div>
        </Panel>
      </div>
    </div>
  );
}

function Kpi({ label, value, sub }: { label: string; value: any; sub: string }) {
  return (
    <div className="card p-3.5">
      <p className="text-[10px] uppercase tracking-[0.12em] text-[var(--text-muted)]">{label}</p>
      <p className="text-2xl font-semibold mt-1">{value}</p>
      <p className="text-[10px] text-emerald-400 mt-0.5">{sub}</p>
    </div>
  );
}

function Panel({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="card p-4">
      <p className="text-[11px] font-medium uppercase tracking-[0.12em] text-[var(--text-muted)] mb-3">{title}</p>
      {children}
    </div>
  );
}

function Stat({ label, value }: { label: string; value: any }) {
  return (
    <div className="flex items-center justify-between border-b border-[var(--border-subtle)] pb-2 last:border-0">
      <span className="text-[12px] text-[var(--text-secondary)]">{label}</span>
      <span className="text-lg font-semibold">{value}</span>
    </div>
  );
}
