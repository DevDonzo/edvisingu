"use client";

import { useEffect, useState } from "react";
import { Search } from "lucide-react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface Lead { id: string; name: string; email: string; source: string; status: string; tags: string[]; created_at: string; }

const STATUS: Record<string, string> = {
  new: "bg-blue-500/8 text-blue-400 border-blue-500/15",
  warm: "bg-amber-500/8 text-amber-400 border-amber-500/15",
  hot: "bg-red-500/8 text-red-400 border-red-500/15",
  member: "bg-emerald-500/8 text-emerald-400 border-emerald-500/15",
};

export default function Leads() {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [filter, setFilter] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API}/leads`).then((r) => r.json()).then((d) => { setLeads(d.leads); setLoading(false); }).catch(() => setLoading(false));
  }, []);

  const filtered = leads.filter((l) => l.name.toLowerCase().includes(filter.toLowerCase()) || l.email.toLowerCase().includes(filter.toLowerCase()));

  return (
    <div className="animate-in">
      <div className="flex items-end justify-between mb-5">
        <div>
          <h1 className="text-xl font-semibold tracking-tight">Leads</h1>
          <p className="text-[12px] text-[var(--text-muted)] mt-0.5">Pipeline from content, referrals, and platforms</p>
        </div>
        <span className="font-mono text-[11px] text-[var(--text-muted)]">{leads.length} contacts</span>
      </div>

      <div className="relative mb-4">
        <Search size={13} className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--text-muted)]" />
        <input value={filter} onChange={(e) => setFilter(e.target.value)} placeholder="Search..." className="input-field pl-8" />
      </div>

      <div className="card overflow-hidden">
        <table className="w-full text-left">
          <thead>
            <tr className="border-b border-[var(--border-subtle)]">
              {["Name", "Email", "Source", "Status", "Tags", "Date"].map((h) => (
                <th key={h} className="px-4 py-2.5 text-[9px] font-medium uppercase tracking-[0.12em] text-[var(--text-muted)]">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={6} className="px-4 py-8 text-center text-[12px] text-[var(--text-muted)]">Loading...</td></tr>
            ) : filtered.map((lead) => (
              <tr key={lead.id} className="border-b border-[var(--border-subtle)] last:border-0 hover:bg-[var(--bg-surface)]/30 transition-colors">
                <td className="px-4 py-2.5 text-[12px] font-medium">{lead.name}</td>
                <td className="px-4 py-2.5 font-mono text-[11px] text-[var(--text-secondary)]">{lead.email}</td>
                <td className="px-4 py-2.5 text-[11px] text-[var(--text-secondary)]">{lead.source}</td>
                <td className="px-4 py-2.5">
                  <span className={`badge border ${STATUS[lead.status] ?? ""}`}>{lead.status}</span>
                </td>
                <td className="px-4 py-2.5">
                  <div className="flex flex-wrap gap-1">
                    {lead.tags.map((t) => <span key={t} className="rounded bg-[var(--bg-surface)] px-1.5 py-0.5 text-[9px] text-[var(--text-muted)]">{t}</span>)}
                  </div>
                </td>
                <td className="px-4 py-2.5 text-[10px] text-[var(--text-muted)]">{new Date(lead.created_at).toLocaleDateString("en-US", { month: "short", day: "numeric" })}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
