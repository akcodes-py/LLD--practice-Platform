import { Link, NavLink, useNavigate } from "react-router-dom";
import { useState } from "react";

export function Header() {
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();
  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 z-40">
      <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between gap-4">
        <Link to="/" className="flex items-center gap-2 shrink-0" aria-label="LLD Practice Platform home">
          <img src="/favicon.svg" alt="LLD Practice Platform logo" className="w-8 h-8" />
          <span className="font-bold text-ink-900 text-base sm:text-lg tracking-tight">
            LLD Practice <span className="text-brand-600">Platform</span>
          </span>
        </Link>
        <nav className="hidden md:flex items-center gap-6 text-sm font-medium" aria-label="Primary">
          <NavLink to="/problems" className={({ isActive }) => (isActive ? "text-brand-600" : "text-ink-600 hover:text-ink-900")}>
            Problems
          </NavLink>
          <NavLink to="/history" className={({ isActive }) => (isActive ? "text-brand-600" : "text-ink-600 hover:text-ink-900")}>
            My attempts
          </NavLink>
          <button className="btn-primary !px-4 !py-2" onClick={() => navigate("/problems")}>
            Start practicing
          </button>
        </nav>
        <button
          className="md:hidden inline-flex items-center justify-center w-10 h-10 rounded-lg border border-slate-300"
          aria-expanded={open}
          aria-controls="mobile-menu"
          aria-label={open ? "Close menu" : "Open menu"}
          onClick={() => setOpen((v) => !v)}
        >
          <span aria-hidden="true" className="text-xl leading-none">{open ? "✕" : "☰"}</span>
        </button>
      </div>
      {open && (
        <nav id="mobile-menu" className="md:hidden border-t border-slate-200 bg-white px-4 py-3 flex flex-col gap-1" aria-label="Mobile">
          <Link to="/problems" onClick={() => setOpen(false)} className="py-2 px-2 rounded-lg hover:bg-slate-100 font-medium">
            Problems
          </Link>
          <Link to="/history" onClick={() => setOpen(false)} className="py-2 px-2 rounded-lg hover:bg-slate-100 font-medium">
            My attempts
          </Link>
          <Link to="/problems" onClick={() => setOpen(false)} className="btn-primary mt-2">
            Start practicing
          </Link>
        </nav>
      )}
    </header>
  );
}

export function Footer() {
  const year = new Date().getFullYear(); // keep copyright year current
  return (
    <footer className="border-t border-slate-200 bg-white mt-16">
      <div className="max-w-6xl mx-auto px-4 py-8 grid gap-6 sm:grid-cols-3 text-sm">
        <div>
          <p className="font-bold text-ink-900">LLD Practice Platform</p>
          <p className="text-ink-500 mt-1">Structured low-level design practice with explainable, rubric-based feedback.</p>
        </div>
        <nav aria-label="Footer">
          <p className="font-semibold mb-2">Practice</p>
          <ul className="space-y-1">
            <li><Link className="text-ink-600 hover:text-ink-900 hover:underline" to="/problems">All problems</Link></li>
            <li><Link className="text-ink-600 hover:text-ink-900 hover:underline" to="/history">My attempts</Link></li>
          </ul>
        </nav>
        <nav aria-label="Legal">
          <p className="font-semibold mb-2">About</p>
          <ul className="space-y-1">
            <li><Link className="text-ink-600 hover:text-ink-900 hover:underline" to="/privacy">Privacy policy</Link></li>
            <li><Link className="text-ink-600 hover:text-ink-900 hover:underline" to="/terms">Terms of use</Link></li>
          </ul>
        </nav>
      </div>
      <div className="border-t border-slate-100">
        <p className="max-w-6xl mx-auto px-4 py-4 text-xs text-ink-500">© {year} LLD Practice Platform (course prototype). Submissions stay in your local backend.</p>
      </div>
    </footer>
  );
}

export function StatusBadge({ status }: { status: string }) {
  const styles: Record<string, string> = {
    draft: "bg-slate-100 text-slate-700 border-slate-300",
    submitted: "bg-blue-50 text-blue-800 border-blue-300",
    evaluating: "bg-amber-50 text-amber-800 border-amber-300",
    completed: "bg-green-50 text-green-800 border-green-300",
    failed: "bg-red-50 text-red-800 border-red-300",
  };
  return (
    <span className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold ${styles[status] ?? styles.draft}`}>
      {status}
    </span>
  );
}

export function ScoreBar({ score }: { score: number }) {
  const pct = Math.max(0, Math.min(100, score));
  const color = pct >= 75 ? "bg-green-600" : pct >= 50 ? "bg-brand-500" : "bg-red-500";
  return (
    <div className="flex items-center gap-3" role="img" aria-label={`Score ${score} out of 100`}>
      <div className="flex-1 h-2.5 rounded-full bg-slate-200 overflow-hidden">
        <div className={`h-full rounded-full ${color}`} style={{ width: `${pct}%` }} />
      </div>
      <span className="font-mono font-bold text-lg tabular-nums">{score}</span>
      <span className="text-xs text-ink-500">/100</span>
    </div>
  );
}

export function EmptyState({ title, body, action }: { title: string; body: string; action?: React.ReactNode }) {
  return (
    <div className="card p-8 text-center max-w-xl mx-auto">
      <h2 className="font-bold text-lg">{title}</h2>
      <p className="text-ink-600 text-sm mt-2">{body}</p>
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}

export function Alert({ kind, children }: { kind: "success" | "error" | "info"; children: React.ReactNode }) {
  const cls =
    kind === "success"
      ? "bg-green-50 border-green-300 text-green-900"
      : kind === "error"
        ? "bg-red-50 border-red-300 text-red-900"
        : "bg-blue-50 border-blue-300 text-blue-900";
  const role = kind === "error" ? "alert" : "status";
  return (
    <div role={role} className={`border rounded-lg px-4 py-3 text-sm ${cls}`}>
      {children}
    </div>
  );
}
