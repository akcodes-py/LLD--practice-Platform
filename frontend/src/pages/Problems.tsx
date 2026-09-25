import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Alert, EmptyState } from "../components/chrome";
import { api, type ProblemSummary } from "../lib/api";
import { usePageMeta } from "../lib/meta";

export function Problems() {
  usePageMeta("Problems — LLD Practice Platform", "Browse 5 low-level design problems: parking lot, elevator, vending machine, library, food ordering.");
  const [problems, setProblems] = useState<ProblemSummary[] | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api.problems().then(setProblems).catch(() => setError("Could not load problems. Is the backend running on port 8000?"));
  }, []);

  if (error) return <div className="max-w-4xl mx-auto px-4 py-10"><Alert kind="error">{error}</Alert></div>;
  if (!problems) return <p className="max-w-4xl mx-auto px-4 py-10 text-ink-600" role="status">Loading problems…</p>;
  if (problems.length === 0)
    return (
      <div className="max-w-4xl mx-auto px-4 py-10">
        <EmptyState title="No problems yet" body="The backend returned an empty catalog. Run `python manage.py seed_problems`." />
      </div>
    );

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold tracking-tight">Choose a problem</h1>
      <p className="text-ink-600 text-sm mt-1">Each brief includes requirements, constraints, design considerations, and edge cases.</p>
      <div className="mt-6 grid gap-4 md:grid-cols-2">
        {problems.map((p) => (
          <article key={p.slug} className="card p-5 flex flex-col">
            <div className="flex items-center gap-2 text-xs">
              <span className="font-semibold uppercase tracking-wide bg-slate-100 border border-slate-200 rounded-full px-2.5 py-0.5">{p.difficulty}</span>
              <span className="text-ink-500">≈ {p.estimated_minutes} min</span>
            </div>
            <h2 className="mt-2 font-bold text-lg">
              <Link to={`/problems/${p.slug}`} className="hover:text-brand-600 hover:underline">{p.title}</Link>
            </h2>
            <p className="mt-1 text-sm text-ink-600 flex-1">{p.summary}</p>
            <div className="mt-3 flex flex-wrap gap-1.5" aria-label="Tags">
              {p.tags.map((t) => (
                <span key={t} className="text-xs bg-brand-50 text-brand-700 border border-brand-100 rounded-full px-2 py-0.5">{t}</span>
              ))}
            </div>
            <Link to={`/problems/${p.slug}`} className="btn-secondary mt-4 self-start">Open brief</Link>
          </article>
        ))}
      </div>
    </div>
  );
}
