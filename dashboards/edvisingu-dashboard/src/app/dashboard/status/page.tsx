"use client";

import { useEffect, useState } from "react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface Service { name: string; port: number; status: string; latency_ms: number; }

export default function Status() {
  const [data, setData] = useState<{ services: Service[]; up: number; total: number; uptime_percent: number } | null>(null);
  const [loading, setLoading] = useState(true);

  const load = () => {
    fetch(`${API}/monitoring`).then((r) => r.json()).then((d) => { setData(d); setLoading(false); }).catch(() => setLoading(false));
  };

  useEffect(() => { load(); const t = setInterval(load, 15000); return () => clearInterval(t); }, []);

  return (
    <div className="animate-in">
      <div className="flex items-end justify-between mb-5">
        <div>
          <h1 className="text-xl font-semibold tracking-tight">System Status</h1>
          <p className="text-[12px] text-[var(--text-muted)] mt-0.5">Live health across the fleet · auto-refresh 15s</p>
        </div>
        {data && (
          <div className="flex items-center gap-2 badge bg-[var(--success-dim)] border border-emerald-500/20 text-emerald-400">
            <span className="dot dot-live" /> {data.up}/{data.total} up · {data.uptime_percent}%
          </div>
        )}
      </div>

      {loading ? (
        <p className="text-[12px] text-[var(--text-muted)]">Loading...</p>
      ) : !data ? (
        <p className="text-[12px] text-[var(--text-muted)]">API offline.</p>
      ) : (
        <div className="grid grid-cols-3 gap-2.5">
          {data.services.map((s) => (
            <div key={s.name} className="card p-3 flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <span className={`dot ${s.status === "up" ? "dot-live" : "bg-red-500"}`} />
                <div>
                  <p className="text-[12px] font-medium">{s.name}</p>
                  <p className="font-mono text-[10px] text-[var(--text-muted)]">:{s.port}</p>
                </div>
              </div>
              <span className="font-mono text-[10px] text-[var(--text-muted)]">{s.latency_ms}ms</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
