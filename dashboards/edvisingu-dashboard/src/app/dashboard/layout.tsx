"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboard, MessageSquare, Sparkles, Users, Activity, GraduationCap, FileText, BarChart3, HeartPulse } from "lucide-react";

const nav = [
  { href: "/dashboard", label: "Overview", icon: LayoutDashboard },
  { href: "/dashboard/hermes", label: "Hermes", icon: MessageSquare },
  { href: "/dashboard/content", label: "Content", icon: Sparkles },
  { href: "/dashboard/advisor", label: "Advisor", icon: GraduationCap },
  { href: "/dashboard/credihire", label: "CrediHire", icon: FileText },
  { href: "/dashboard/leads", label: "Leads", icon: Users },
  { href: "/dashboard/analytics", label: "Analytics", icon: BarChart3 },
  { href: "/dashboard/fleet", label: "Fleet", icon: Activity },
  { href: "/dashboard/status", label: "Status", icon: HeartPulse },
];

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <div className="flex h-screen overflow-hidden">
      <aside className="w-56 flex flex-col border-r border-[var(--border-subtle)] bg-[var(--bg-elevated)]">
        {/* Brand */}
        <div className="px-5 py-6">
          <p className="text-[13px] font-semibold tracking-tight">Hamza Paracha</p>
          <p className="text-[10px] font-medium uppercase tracking-[0.15em] text-[var(--text-muted)] mt-0.5">Command Center</p>
        </div>

        {/* Nav */}
        <nav className="flex-1 px-3 space-y-0.5">
          {nav.map(({ href, label, icon: Icon }) => {
            const active = pathname === href;
            return (
              <Link
                key={href}
                href={href}
                className={`flex items-center gap-2.5 rounded-lg px-3 py-2 text-[12.5px] font-medium transition-all ${
                  active
                    ? "bg-[var(--accent-dim)] text-[var(--accent)]"
                    : "text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-surface)]"
                }`}
              >
                <Icon size={14} strokeWidth={active ? 2 : 1.5} />
                {label}
              </Link>
            );
          })}
        </nav>

        {/* Footer */}
        <div className="px-5 py-4 border-t border-[var(--border-subtle)]">
          <div className="flex items-center gap-2">
            <span className="dot dot-live" />
            <span className="text-[10px] text-[var(--text-muted)]">25 agents · operational</span>
          </div>
        </div>
      </aside>

      <main className="flex-1 overflow-y-auto">
        <div className="max-w-[1100px] mx-auto px-8 py-8">
          {children}
        </div>
      </main>
    </div>
  );
}
