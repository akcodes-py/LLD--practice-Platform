import { useEffect, useRef, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { Alert } from "../components/chrome";
import { api, type Attempt } from "../lib/api";
import { usePageMeta } from "../lib/meta";

const FIELDS = [
  { key: "requirements_assumptions", label: "Requirements & assumptions", hint: "Map each functional requirement to a design element; state what you assumed.", min: 40 },
  { key: "classes_responsibilities", label: "Classes & responsibilities", hint: "One job per class. Name what each class owns and what it does NOT own.", min: 60 },
  { key: "relationships_interfaces", label: "Relationships & interfaces", hint: "Key method signatures, who depends on whom, which dependencies are interfaces.", min: 30 },
  { key: "workflows", label: "Workflows", hint: "Entry/exit or request flows step by step, with the reasoning behind choices.", min: 30 },
  { key: "tradeoffs", label: "Trade-offs", hint: "One alternative you considered, why you chose this design, and what changes easily.", min: 30 },
  { key: "edge_cases", label: "Edge cases", hint: "Concurrency, failures, invalid input — and how each is handled or tested.", min: 30 },
] as const;

type FieldKey = (typeof FIELDS)[number]["key"];

export function AttemptEditor() {
  const { id = "" } = useParams();
  const navigate = useNavigate();
  const [attempt, setAttempt] = useState<Attempt | null>(null);
  const [draft, setDraft] = useState<Record<FieldKey, string>>({} as Record<FieldKey, string>);
  const [errors, setErrors] = useState<Record<string, string[]>>({});
  const [notice, setNotice] = useState<{ kind: "success" | "error" | "info"; text: string } | null>(null);
  const [saving, setSaving] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const saveTimer = useRef<number | undefined>(undefined);
  usePageMeta("Write your design — LLD Practice Platform", "Draft your classes, interfaces, workflows, trade-offs, and edge cases.");

  useEffect(() => {
    api.attempt(id).then((a) => {
      setAttempt(a);
      setDraft({
        requirements_assumptions: a.requirements_assumptions,
        classes_responsibilities: a.classes_responsibilities,
        relationships_interfaces: a.relationships_interfaces,
        workflows: a.workflows,
        tradeoffs: a.tradeoffs,
        edge_cases: a.edge_cases,
      });
      if (a.status !== "draft") navigate(`/attempts/${a.id}/review`, { replace: true });
    }).catch(() => setNotice({ kind: "error", text: "Could not load this attempt. It may not exist or the backend is down." }));
    return () => window.clearTimeout(saveTimer.current);
  }, [id, navigate]);

  function edit(key: FieldKey, value: string) {
    setDraft((d) => ({ ...d, [key]: value }));
    window.clearTimeout(saveTimer.current);
    saveTimer.current = window.setTimeout(() => saveDraft({ [key]: value } as Partial<Attempt>), 900);
  }

  async function saveDraft(patch?: Partial<Attempt>) {
    if (!attempt || attempt.status !== "draft") return;
    setSaving(true);
    try {
      const updated = await api.updateAttempt(attempt.id, (patch ?? draft) as Partial<Attempt>);
      setAttempt(updated);
      setNotice({ kind: "success", text: "Draft saved." });
    } catch {
      setNotice({ kind: "error", text: "Could not save the draft. Your text is still in the editor — try again." });
    } finally {
      setSaving(false);
    }
  }

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    // Lightweight bot protection: hidden honeypot must stay empty (no CAPTCHA for a local prototype).
    const honeypot = (document.getElementById("company-website") as HTMLInputElement | null)?.value;
    if (honeypot) {
      setNotice({ kind: "error", text: "Submission blocked as spam. Please submit from the visible form." });
      return;
    }
    if (!attempt) return;
    setSubmitting(true);
    setErrors({});
    setNotice(null);
    try {
      await api.updateAttempt(attempt.id, draft as Partial<Attempt>);
      await api.submitAttempt(attempt.id);
      // Evaluation is now async — navigate to review immediately; the review
      // page polls /api/attempts/<id>/status/ until evaluation completes.
      navigate(`/attempts/${attempt.id}/review`);
    } catch (err: unknown) {
      const e = err as { code?: string; details?: Record<string, string[]>; message?: string };
      if (e.code === "validation_error" && e.details) {
        setErrors(e.details);
        setNotice({ kind: "error", text: "Some sections need more detail before evaluation. See the messages below." });
      } else {
        setNotice({ kind: "error", text: e.message ?? "Submission failed. Your draft is saved — try again." });
      }
    } finally {
      setSubmitting(false);
    }
  }

  if (!attempt) return <p className="max-w-4xl mx-auto px-4 py-10 text-ink-600" role="status">Loading editor…</p>;

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <Link to={`/problems/${attempt.problem_slug}`} className="text-sm text-ink-600 hover:text-ink-900 hover:underline">← Back to {attempt.problem_title} brief</Link>
      <div className="mt-2 flex items-center justify-between flex-wrap gap-2">
        <h1 className="text-2xl font-bold tracking-tight">Design: {attempt.problem_title}</h1>
        <span className="text-xs text-ink-500" role="status">{saving ? "Saving…" : "Draft auto-saves as you type"}</span>
      </div>
      {notice && <div className="mt-3"><Alert kind={notice.kind}>{notice.text}</Alert></div>}

      <form onSubmit={submit} className="mt-6 space-y-5" noValidate>
        {/* Honeypot field for spam/bot protection; hidden from sighted users and screen readers. */}
        <input id="company-website" name="company-website" type="text" tabIndex={-1} autoComplete="off" className="hidden" aria-hidden="true" />

        {FIELDS.map((f) => {
          const value = draft[f.key] ?? "";
          const fieldErrors = errors[f.key] ?? [];
          const tooShort = value.trim().length > 0 && value.trim().length < f.min;
          return (
            <div key={f.key} className="card p-5">
              <label className="field-label" htmlFor={f.key}>{f.label}</label>
              <p className="field-hint">{f.hint} Minimum {f.min} characters.</p>
              <textarea
                id={f.key}
                value={value}
                onChange={(e) => edit(f.key, e.target.value)}
                rows={6}
                minLength={f.min}
                required
                aria-invalid={fieldErrors.length > 0}
                aria-describedby={`${f.key}-count ${f.key}-err`}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm leading-relaxed font-mono focus:border-brand-500"
                placeholder="Write concretely: names, responsibilities, and reasons — not placeholders."
              />
              <div className="mt-1 flex justify-between text-xs">
                <span id={`${f.key}-err`}>{fieldErrors.map((m) => <span key={m} className="field-error block">{m}</span>)}</span>
                <span id={`${f.key}-count`} className={tooShort ? "text-amber-700 font-semibold" : "text-ink-500"}>
                  {value.trim().length}/{f.min} min
                </span>
              </div>
            </div>
          );
        })}

        <div className="flex flex-wrap gap-3">
          <button type="button" className="btn-secondary" onClick={() => saveDraft()} disabled={saving}>Save draft</button>
          <button type="submit" className="btn-primary" disabled={submitting}>{submitting ? "Submitting…" : "Submit for feedback"}</button>
        </div>
      </form>
    </div>
  );
}
