import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Alert, EmptyState, StatusBadge } from "../components/chrome";
import { api, type Attempt } from "../lib/api";
import { usePageMeta } from "../lib/meta";

export function History() {
  usePageMeta("My attempts — LLD Practice Platform", "Every draft, submission, score, and retry in one place.");
  const [attempts, setAttempts] = useState<Attempt[] | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api.attempts().then(setAttempts).catch(() => setError("Could not load attempt history. Is the backend running?"));
  }, []);

  if (error) return <div className="max-w-4xl mx-auto px-4 py-10"><Alert kind="error">{error}</Alert></div>;
  if (!attempts) return <p className="max-w-4xl mx-auto px-4 py-10 text-ink-600" role="status">Loading history…</p>;
  if (attempts.length === 0)
    return (
      <div className="max-w-4xl mx-auto px-4 py-10">
        <EmptyState
          title="No attempts yet"
          body="You have not started any design. Pick a problem and submit your first attempt — feedback appears here."
          action={<Link to="/problems" className="btn-primary">Browse problems</Link>}
        />
      </div>
    );

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold tracking-tight">My attempts ({attempts.length})</h1>
      <p className="text-sm text-ink-600 mt-1">Newest first. Retries create new rows — nothing is overwritten.</p>
      <ul className="mt-5 space-y-3">
        {attempts.map((a) => (
          <li key={a.id} className="card px-4 py-3 flex items-center justify-between gap-3 flex-wrap">
            <div>
              <p className="font-semibold">{a.problem_title}</p>
              <div className="mt-1 flex items-center gap-2 text-xs text-ink-500">
                <StatusBadge status={a.status} />
                <span>{new Date(a.created_at).toLocaleString()}</span>
                {a.evaluation?.total_score != null && <span className="font-mono font-bold text-ink-900">{a.evaluation.total_score}/100</span>}
              </div>
            </div>
            {a.status === "draft" ? (
              <Link className="btn-secondary !px-3 !py-1.5 text-sm" to={`/attempts/${a.id}`}>Continue</Link>
            ) : (
              <Link className="btn-secondary !px-3 !py-1.5 text-sm" to={`/attempts/${a.id}/review`}>Review</Link>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}
