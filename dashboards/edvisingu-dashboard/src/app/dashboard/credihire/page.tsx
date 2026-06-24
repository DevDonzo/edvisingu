"use client";

import { useState } from "react";
import { FileText, CheckCircle2, AlertTriangle, Wrench } from "lucide-react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface Analysis {
  ats_score: number;
  overall_grade: string;
  strengths: string[];
  weaknesses: string[];
  improvements: string[];
  keyword_gaps: string[];
}

export default function CrediHire() {
  const [resume, setResume] = useState("");
  const [result, setResult] = useState<Analysis | null>(null);
  const [loading, setLoading] = useState(false);

  const analyze = async () => {
    if (!resume.trim() || loading) return;
    setLoading(true);
    setResult(null);
    try {
      const res = await fetch(`${API}/credihire/analyze`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ resume_text: resume }) });
      setResult(await res.json());
    } catch {
      /* offline */
    }
    setLoading(false);
  };

  const scoreColor = result && result.ats_score >= 80 ? "text-emerald-400" : result && result.ats_score >= 65 ? "text-amber-400" : "text-red-400";

  return (
    <div className="animate-in">
      <div className="mb-5">
        <h1 className="text-xl font-semibold tracking-tight">CrediHire Resume Engine</h1>
        <p className="text-[12px] text-[var(--text-muted)] mt-0.5">ATS scoring & optimization · hermes-credihire</p>
      </div>

      <div className="grid grid-cols-2 gap-5">
        <div className="card p-4">
          <label className="text-[11px] font-medium uppercase tracking-[0.12em] text-[var(--text-muted)]">Paste resume text</label>
          <textarea
            value={resume}
            onChange={(e) => setResume(e.target.value)}
            placeholder="Paste your resume here..."
            className="input-field mt-2 h-72 w-full resize-none font-mono text-[12px]"
          />
          <button onClick={analyze} disabled={loading || !resume.trim()} className="btn-accent mt-3 w-full disabled:opacity-30">
            {loading ? "Analyzing..." : "Analyze Resume"}
          </button>
        </div>

        <div className="card p-4">
          {!result ? (
            <div className="flex h-full flex-col items-center justify-center text-center">
              <div className="h-10 w-10 rounded-xl bg-[var(--accent-dim)] border border-[var(--accent-border)] flex items-center justify-center mb-3">
                <FileText size={18} className="text-[var(--accent)]" />
              </div>
              <p className="text-[12px] text-[var(--text-muted)] max-w-[200px]">Results appear here: ATS score, strengths, gaps, and fixes.</p>
            </div>
          ) : (
            <div className="space-y-4 animate-up">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-[10px] uppercase tracking-[0.12em] text-[var(--text-muted)]">ATS Score</p>
                  <p className={`text-3xl font-semibold ${scoreColor}`}>{result.ats_score}<span className="text-[var(--text-muted)] text-base">/100</span></p>
                </div>
                <span className="badge border border-[var(--border)] text-[var(--text-secondary)] text-base">{result.overall_grade}</span>
              </div>

              <Section icon={CheckCircle2} color="text-emerald-400" title="Strengths" items={result.strengths} />
              <Section icon={AlertTriangle} color="text-amber-400" title="Weaknesses" items={result.weaknesses} />
              <Section icon={Wrench} color="text-[var(--accent)]" title="Improvements" items={result.improvements} />

              {result.keyword_gaps && (
                <div>
                  <p className="text-[10px] uppercase tracking-[0.12em] text-[var(--text-muted)] mb-1.5">Keyword Gaps</p>
                  <div className="flex flex-wrap gap-1.5">
                    {result.keyword_gaps.map((k) => <span key={k} className="rounded bg-red-500/8 border border-red-500/15 px-2 py-0.5 text-[10px] text-red-400">{k}</span>)}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function Section({ icon: Icon, color, title, items }: { icon: any; color: string; title: string; items: string[] }) {
  return (
    <div>
      <div className="flex items-center gap-1.5 mb-1.5">
        <Icon size={12} className={color} />
        <p className="text-[10px] uppercase tracking-[0.12em] text-[var(--text-muted)]">{title}</p>
      </div>
      <ul className="space-y-1">
        {items.map((it, i) => <li key={i} className="text-[12px] text-[var(--text-secondary)] pl-3.5">· {it}</li>)}
      </ul>
    </div>
  );
}
