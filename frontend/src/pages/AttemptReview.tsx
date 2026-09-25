import { useCallback, useEffect, useRef, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { Alert, EmptyState, ScoreBar, StatusBadge } from "../components/chrome";
import { api, criterionLabel, type Attempt } from "../lib/api";
import { usePageMeta } from "../lib/meta";

const TERMINAL_STATUSES = new Set(["completed", "failed"]);
const POLL_INTERVAL_MS = 1500;

export function AttemptReview() {
  const { id = "" } = useParams();
  const navigate = useNavigate();
  const [attempt, setAttempt] = useState<Attempt | null>(null);
  const [error, setError] = useState("");
  const [action, setAction] = useState("");
  const [notice, setNotice] = useState<{ kind: "success" | "error"; text: string } | null>(null);
  const pollRef = useRef<number | undefined>(undefined);
  usePageMeta("Feedback — LLD Practice Platform", "Criterion-level feedback with evidence, concerns, and next steps for your design.");

  const stopPolling = () => window.clearInterval(pollRef.current);

  const load = useCallback(() => {
    api.attempt(id).then((a) => {
      setAttempt(a);
      // If evaluation is still in-progress, start polling the lightweight status endpoint.
      if (!TERMINAL_STATUSES.has(a.status)) {
        pollRef.current = window.setInterval(async () => {
          try {
            const updated = await api.pollAttemptStatus(id);
            setAttempt(updated);
            if (TERMINAL_STATUSES.has(updated.status)) stopPolling();
          } catch {
            // Network hiccup — keep polling; hard errors surface via attempt load above.
          }
        }, POLL_INTERVAL_MS);
      }
    }).catch(() => setError("Could not load this attempt."));
  }, [id]);

  useEffect(() => { load(); return stopPolling; }, [load]);

  async function retry() {
    setAction("retry");
    try {
      const next = await api.retryAttempt(id);
      setNotice({ kind: "success", text: "New draft created. Your previous attempt is preserved in history." });
      navigate(`/attempts/${next.id}`);
    } catch {
      setNotice({ kind: "error", text: "Could not create a retry draft. Try again." });
    } finally {
      setAction("");
    }
  }

  async function reEvaluate() {
    setAction("reeval");
    try {
      const updated = await api.reEvaluate(id);
      setAttempt(updated);
      setNotice({ kind: "success", text: "Re-evaluation finished." });
    } catch (e: unknown) {
      setNotice({ kind: "error", text: (e as Error).message ?? "Re-evaluation failed." });
    } finally {
      setAction("");
    }
  }

  if (error) return <div className="max-w-4xl mx-auto px-4 py-10"><Alert kind="error">{error}</Alert></div>;
  if (!attempt) return <p className="max-w-4xl mx-auto px-4 py-10 text-ink-600" role="status">Loading feedback…</p>;

  const ev = attempt.evaluation;

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <div className="flex items-center justify-between flex-wrap gap-2">
        <Link to={`/problems/${attempt.problem_slug}`} className="text-sm text-ink-600 hover:text-ink-900 hover:underline">← {attempt.problem_title}</Link>
        <StatusBadge status={attempt.status} />
      </div>
      <h1 className="mt-2 text-2xl font-bold tracking-tight">Feedback: {attempt.problem_title}</h1>
      {notice && <div className="mt-3"><Alert kind={notice.kind}>{notice.text}</Alert></div>}

      {(attempt.status === "submitted" || attempt.status === "evaluating") && (
        <div className="mt-4"><Alert kind="info">Evaluation in progress… this refreshes automatically.</Alert></div>
      )}

      {!ev && attempt.status === "draft" && (
        <div className="mt-4">
          <EmptyState title="Not submitted yet" body="This attempt is still a draft." action={<Link className="btn-primary" to={`/attempts/${attempt.id}`}>Continue editing</Link>} />
        </div>
      )}

      {ev?.state === "failed" && (
        <div className="mt-4 space-y-3">
          <Alert kind="error">Evaluation failed and your submission is intact: {ev.error || "unknown evaluator error."} Nothing was deleted.</Alert>
          <button className="btn-primary" onClick={reEvaluate} disabled={action === "reeval"}>
            {action === "reeval" ? "Re-evaluating…" : "Try evaluation again"}
          </button>
        </div>
      )}

      {ev?.state === "completed" && (
        <div className="mt-6 space-y-5">
          <section className="card p-5" aria-label="Overall score">
            <div className="flex items-center justify-between flex-wrap gap-2">
              <h2 className="font-bold">Overall</h2>
              <span className="text-xs font-semibold uppercase tracking-wide bg-slate-100 border border-slate-200 rounded-full px-2.5 py-0.5">
                {ev.provider === "llm" ? "AI review" : "Rule-based review"}
              </span>
            </div>
            <div className="mt-3"><ScoreBar score={ev.total_score ?? 0} /></div>
            <p className="mt-3 text-sm leading-relaxed">{ev.overall_feedback}</p>
          </section>

          <section aria-label="Rubric breakdown">
            <h2 className="font-bold text-lg">Rubric breakdown</h2>
            <div className="mt-3 space-y-3">
              {ev.rubric_results.map((r) => (
                <article key={r.criterion} className="card p-5">
                  <div className="flex items-center justify-between gap-3 flex-wrap">
                    <h3 className="font-semibold">{criterionLabel(r.criterion)}</h3>
                    <span className="font-mono font-bold text-sm tabular-nums" aria-label={`${r.score} out of 10`}>{r.score}/10</span>
                  </div>
                  <div className="mt-1 h-1.5 rounded-full bg-slate-100 overflow-hidden" aria-hidden="true">
                    <div className={`h-full rounded-full ${r.score >= 7 ? "bg-green-600" : r.score >= 5 ? "bg-brand-500" : "bg-red-500"}`} style={{ width: `${r.score * 10}%` }} />
                  </div>
                  <dl className="mt-3 space-y-2 text-sm">
                    <div><dt className="font-semibold text-ink-500 text-xs uppercase tracking-wide">Evidence</dt><dd className="mt-0.5">{r.evidence}</dd></div>
                    <div><dt className="font-semibold text-ink-500 text-xs uppercase tracking-wide">Concern</dt><dd className="mt-0.5">{r.concern}</dd></div>
                    <div><dt className="font-semibold text-ink-500 text-xs uppercase tracking-wide">Next step</dt><dd className="mt-0.5">{r.suggestion}</dd></div>
                  </dl>
                  <p className="mt-2 text-xs text-ink-500">Confidence: {Math.round(r.confidence * 100)}%</p>
                </article>
              ))}
            </div>
          </section>

          <div className="grid gap-4 md:grid-cols-2">
            <section className="card p-5" aria-label="Strengths">
              <h2 className="font-bold">Strengths</h2>
              <ul className="mt-2 text-sm space-y-1.5 list-disc pl-5">{ev.strengths.map((s, i) => <li key={i}>{s}</li>)}</ul>
            </section>
            <section className="card p-5" aria-label="Improvements">
              <h2 className="font-bold">Focus next</h2>
              <ul className="mt-2 text-sm space-y-1.5 list-disc pl-5">{ev.improvements.map((s, i) => <li key={i}>{s}</li>)}</ul>
            </section>
          </div>

          <div className="flex flex-wrap gap-3">
            <button className="btn-primary" onClick={retry} disabled={action === "retry"}>
              {action === "retry" ? "Creating draft…" : "Retry (keep history)"}
            </button>
            <Link to="/history" className="btn-secondary">Back to history</Link>
          </div>
        </div>
      )}

      <section className="mt-10 card p-5" aria-label="Submitted design">
        <h2 className="font-bold">Your submitted design</h2>
        <div className="mt-3 space-y-3 text-sm">
          {([["Requirements & assumptions", attempt.requirements_assumptions], ["Classes & responsibilities", attempt.classes_responsibilities], ["Relationships & interfaces", attempt.relationships_interfaces], ["Workflows", attempt.workflows], ["Trade-offs", attempt.tradeoffs], ["Edge cases", attempt.edge_cases]] as const).map(([label, value]) => (
            <details key={label} className="border border-slate-200 rounded-lg px-3 py-2">
              <summary className="font-semibold cursor-pointer">{label}</summary>
              <p className="mt-2 whitespace-pre-wrap font-mono text-xs leading-relaxed">{value || "(empty)"}</p>
            </details>
          ))}
        </div>
      </section>
    </div>
  );
}
