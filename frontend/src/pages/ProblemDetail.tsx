import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { Alert, EmptyState, StatusBadge } from "../components/chrome";
import { api, type Attempt, type ProblemDetail } from "../lib/api";
import { usePageMeta } from "../lib/meta";

export function ProblemDetail() {
  const { slug = "" } = useParams();
  const navigate = useNavigate();
  const [problem, setProblem] = useState<ProblemDetail | null>(null);
  const [history, setHistory] = useState<Attempt[]>([]);
  const [error, setError] = useState("");
  const [starting, setStarting] = useState(false);
  const [notice, setNotice] = useState("");
  usePageMeta(
    problem ? `${problem.title} — LLD Practice Platform` : "Problem — LLD Practice Platform",
    problem?.summary ?? "Read the brief, then start a structured design attempt."
  );

  useEffect(() => {
    api.problem(slug).then(setProblem).catch(() => setError("Problem not found or backend unreachable."));
    api.attempts(slug).then(setHistory).catch(() => {});
  }, [slug]);

  async function startAttempt() {
    setStarting(true);
    setNotice("");
    try {
      const attempt = await api.createAttempt(slug);
      navigate(`/attempts/${attempt.id}`);
    } catch {
      setNotice("Could not start an attempt. Check the backend is running and try again.");
    } finally {
      setStarting(false);
    }
  }

  if (error) return <div className="max-w-4xl mx-auto px-4 py-10"><Alert kind="error">{error}</Alert></div>;
  if (!problem) return <p className="max-w-4xl mx-auto px-4 py-10 text-ink-600" role="status">Loading brief…</p>;

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <Link to="/problems" className="text-sm text-ink-600 hover:text-ink-900 hover:underline">← All problems</Link>
      <h1 className="mt-2 text-2xl font-bold tracking-tight">{problem.title}</h1>
      <p className="mt-1 text-sm text-ink-500">{problem.difficulty} · ≈ {problem.estimated_minutes} min · {problem.tags.join(" · ")}</p>
      <p className="mt-4 leading-relaxed">{problem.description}</p>

      <div className="mt-6 grid gap-4 md:grid-cols-2">
        <section className="card p-5" aria-label="Functional requirements">
          <h2 className="font-bold">Functional requirements</h2>
          <ul className="mt-2 space-y-1.5 text-sm list-disc pl-5">
            {problem.functional_requirements.map((r, i) => <li key={i}>{r}</li>)}
          </ul>
        </section>
        <section className="card p-5" aria-label="Constraints">
          <h2 className="font-bold">Constraints</h2>
          <ul className="mt-2 space-y-1.5 text-sm list-disc pl-5">
            {problem.constraints.map((r, i) => <li key={i}>{r}</li>)}
          </ul>
        </section>
        <section className="card p-5" aria-label="Design considerations">
          <h2 className="font-bold">Design considerations</h2>
          <ul className="mt-2 space-y-1.5 text-sm list-disc pl-5">
            {problem.design_considerations.map((r, i) => <li key={i}>{r}</li>)}
          </ul>
        </section>
        <section className="card p-5" aria-label="Edge cases to consider">
          <h2 className="font-bold">Edge cases to consider</h2>
          <ul className="mt-2 space-y-1.5 text-sm list-disc pl-5">
            {problem.edge_cases.map((r, i) => <li key={i}>{r}</li>)}
          </ul>
        </section>
      </div>

      <div className="mt-6 flex flex-wrap gap-3">
        <button className="btn-primary" onClick={startAttempt} disabled={starting}>
          {starting ? "Starting…" : "Start attempt"}
        </button>
        <Link to="/history" className="btn-secondary">View my history</Link>
      </div>
      {notice && <div className="mt-3"><Alert kind="error">{notice}</Alert></div>}

      <section className="mt-10" aria-label="Previous attempts for this problem">
        <h2 className="font-bold text-lg">Your attempts on this problem ({history.length})</h2>
        {history.length === 0 ? (
          <div className="mt-3">
            <EmptyState title="No attempts yet" body="Start your first attempt above. Your drafts, submissions, and feedback will appear here." />
          </div>
        ) : (
          <ul className="mt-3 space-y-2">
            {history.map((a) => (
              <li key={a.id} className="card px-4 py-3 flex items-center justify-between gap-3 flex-wrap">
                <div className="flex items-center gap-3 text-sm">
                  <StatusBadge status={a.status} />
                  <span className="text-ink-500">{new Date(a.created_at).toLocaleString()}</span>
                  {a.evaluation?.total_score != null && (
                    <span className="font-mono font-bold">{a.evaluation.total_score}/100</span>
                  )}
                </div>
                <div className="flex gap-2 text-sm">
                  {a.status === "draft" ? (
                    <Link className="font-semibold text-brand-600 hover:underline" to={`/attempts/${a.id}`}>Continue editing</Link>
                  ) : (
                    <Link className="font-semibold text-brand-600 hover:underline" to={`/attempts/${a.id}/review`}>Review feedback</Link>
                  )}
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
