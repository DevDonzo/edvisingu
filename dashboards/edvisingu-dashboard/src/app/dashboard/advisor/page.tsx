"use client";

import { useState, useRef, useEffect } from "react";
import { ArrowUp, GraduationCap, User } from "lucide-react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface Message { role: "user" | "assistant"; content: string; }

export default function Advisor() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => { endRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages, loading]);

  const send = async () => {
    if (!input.trim() || loading) return;
    const msg = input.trim();
    setInput("");
    setMessages((p) => [...p, { role: "user", content: msg }]);
    setLoading(true);
    try {
      const res = await fetch(`${API}/advisor/chat`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ message: msg }) });
      const data = await res.json();
      setMessages((p) => [...p, { role: "assistant", content: data.response }]);
    } catch {
      setMessages((p) => [...p, { role: "assistant", content: "Connection error — API offline." }]);
    }
    setLoading(false);
  };

  return (
    <div className="flex h-[calc(100vh-7rem)] flex-col animate-in">
      <div className="flex items-center justify-between mb-5">
        <div>
          <h1 className="text-xl font-semibold tracking-tight">Student Advisor</h1>
          <p className="text-[12px] text-[var(--text-muted)] mt-0.5">24/7 academic, income & career guidance · hermes-advisor</p>
        </div>
        <div className="flex items-center gap-1.5 badge bg-[var(--success-dim)] border border-emerald-500/20 text-emerald-400">
          <span className="dot dot-live" /> Active
        </div>
      </div>

      <div className="flex-1 overflow-y-auto rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-primary)] p-5 space-y-5">
        {messages.length === 0 && (
          <div className="flex h-full flex-col items-center justify-center">
            <div className="h-10 w-10 rounded-xl bg-[var(--accent-dim)] border border-[var(--accent-border)] flex items-center justify-center mb-4">
              <GraduationCap size={18} className="text-[var(--accent)]" />
            </div>
            <p className="text-sm font-medium">How can I help you succeed?</p>
            <p className="text-[12px] text-[var(--text-muted)] mt-1 text-center max-w-xs">Courses, OSAP/BSWD, income while studying, work-integrated learning.</p>
            <div className="flex flex-wrap gap-2 mt-5 justify-center">
              {["How do I earn $500/month while studying?", "Help me optimize my OSAP application", "What WIL projects match me?"].map((q) => (
                <button key={q} onClick={() => setInput(q)} className="rounded-lg border border-[var(--border-subtle)] px-3 py-1.5 text-[11px] text-[var(--text-muted)] hover:text-[var(--text-primary)] hover:border-[var(--border)] transition-colors">{q}</button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <div key={i} className={`flex gap-3 animate-up ${msg.role === "user" ? "justify-end" : ""}`}>
            {msg.role === "assistant" && (
              <div className="h-6 w-6 rounded-md bg-[var(--accent-dim)] border border-[var(--accent-border)] flex items-center justify-center shrink-0 mt-0.5">
                <GraduationCap size={11} className="text-[var(--accent)]" />
              </div>
            )}
            <div className={`max-w-[70%] rounded-xl px-4 py-3 ${msg.role === "user" ? "bg-[var(--bg-surface)] border border-[var(--border-subtle)]" : ""}`}>
              <div className="space-y-1.5 text-[13px] leading-[1.7] text-[var(--text-secondary)]">
                {msg.content.split("\n").map((line, j) => (
                  <p key={j} dangerouslySetInnerHTML={{ __html: line.replace(/\*\*(.+?)\*\*/g, '<b class="font-semibold text-[var(--text-primary)]">$1</b>') }} />
                ))}
              </div>
            </div>
            {msg.role === "user" && (
              <div className="h-6 w-6 rounded-md bg-[var(--bg-surface)] border border-[var(--border-subtle)] flex items-center justify-center shrink-0 mt-0.5">
                <User size={11} className="text-[var(--text-muted)]" />
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="flex gap-3 animate-up">
            <div className="h-6 w-6 rounded-md bg-[var(--accent-dim)] border border-[var(--accent-border)] flex items-center justify-center shrink-0">
              <GraduationCap size={11} className="text-[var(--accent)]" />
            </div>
            <div className="flex items-center gap-1 px-3 py-2">
              <div className="h-1 w-1 rounded-full bg-[var(--text-muted)] animate-bounce [animation-delay:0ms]" />
              <div className="h-1 w-1 rounded-full bg-[var(--text-muted)] animate-bounce [animation-delay:150ms]" />
              <div className="h-1 w-1 rounded-full bg-[var(--text-muted)] animate-bounce [animation-delay:300ms]" />
            </div>
          </div>
        )}
        <div ref={endRef} />
      </div>

      <div className="mt-3 flex gap-2">
        <input value={input} onChange={(e) => setInput(e.target.value)} onKeyDown={(e) => e.key === "Enter" && send()} placeholder="Ask the advisor..." className="input-field flex-1" />
        <button onClick={send} disabled={loading || !input.trim()} className="btn-accent disabled:opacity-30 px-3"><ArrowUp size={15} /></button>
      </div>
    </div>
  );
}
