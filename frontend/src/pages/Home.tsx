import { Link } from "react-router-dom";
import { usePageMeta } from "../lib/meta";

const STEPS = [
  { n: "1", title: "Choose a problem", body: "Pick from 5 interview-grade LLD problems with requirements, constraints, and edge cases spelled out." },
  { n: "2", title: "Write a structured design", body: "Six focused sections — assumptions, classes, interfaces, workflows, trade-offs, edge cases." },
  { n: "3", title: "Submit & get feedback", body: "A deterministic rubric scores 8 criteria with evidence quoted from your design and concrete next steps." },
  { n: "4", title: "Review & retry", body: "History is preserved. Retry clones your work into a fresh draft so you can improve without losing evidence." },
];

export function Home() {
  usePageMeta(
    "LLD Practice Platform — Practice Low-Level Design with Explainable Feedback",
    "Practice low-level design on classic problems. Structured submissions, rubric-based feedback, attempt history, and retry."
  );
  return (
    <div>
      <section className="max-w-6xl mx-auto px-4 pt-12 pb-10 grid gap-8 md:grid-cols-2 md:items-center">
        <div>
          <p className="text-xs font-bold uppercase tracking-widest text-brand-600">Low-level design practice</p>
          <h1 className="mt-2 text-3xl sm:text-4xl font-bold tracking-tight leading-tight">
            Know whether your LLD is actually good — and why.
          </h1>
          <p className="mt-3 text-ink-600 leading-relaxed">
            LLD practice is easy to start and hard to evaluate. This platform gives you a tight loop:
            attempt a real problem, submit a structured design, and get criterion-level feedback
            with evidence from your own words — not a single mystery score.
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <Link to="/problems" className="btn-primary">Start practicing</Link>
            <Link to="/history" className="btn-secondary">Review my attempts</Link>
          </div>
          <p className="mt-4 text-xs text-ink-500">5 problems · No sign-up · Rule-based review works offline · No data leaves your machine.</p>
        </div>
        <div className="card p-5" aria-label="Example feedback preview">
          <p className="text-xs font-bold uppercase tracking-widest text-ink-500">Example feedback</p>
          <div className="mt-3 space-y-3 text-sm">
            <div className="border-l-4 border-green-600 pl-3">
              <p className="font-semibold">Class responsibilities — 8/10</p>
              <p className="text-ink-600">“ParkingLot delegates allocation to a Strategy…” Clear ownership, no god object.</p>
            </div>
            <div className="border-l-4 border-amber-500 pl-3">
              <p className="font-semibold">Coupling — 5/10</p>
              <p className="text-ink-600">Payment depends on concrete classes. Next: depend on an IPayment interface.</p>
            </div>
            <div className="border-l-4 border-red-500 pl-3">
              <p className="font-semibold">Edge cases — 3/10</p>
              <p className="text-ink-600">Concurrency mentioned but not handled. Next: guard the last-spot allocation.</p>
            </div>
          </div>
        </div>
      </section>

      <section className="max-w-6xl mx-auto px-4 py-6" aria-label="How it works">
        <h2 className="text-xl font-bold">How the practice loop works</h2>
        <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {STEPS.map((s) => (
            <article key={s.n} className="card p-5">
              <p className="w-8 h-8 rounded-full bg-ink-900 text-white font-bold flex items-center justify-center" aria-hidden="true">{s.n}</p>
              <h3 className="mt-3 font-semibold">{s.title}</h3>
              <p className="mt-1 text-sm text-ink-600">{s.body}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="max-w-6xl mx-auto px-4 py-6" aria-label="What feedback covers">
        <div className="card p-6 grid gap-4 md:grid-cols-2">
          <div>
            <h2 className="text-xl font-bold">Feedback you can act on</h2>
            <p className="mt-2 text-sm text-ink-600 leading-relaxed">
              Every criterion returns a score, evidence quoted from your submission, the concern,
              an actionable suggestion, and a confidence note. Alternative valid designs are welcome —
              you are judged on stated responsibilities, interfaces, and trade-offs, not on matching
              one reference solution.
            </p>
          </div>
          <ul className="text-sm grid grid-cols-1 sm:grid-cols-2 gap-2">
            {["Requirement understanding", "Class responsibilities", "Coupling & dependencies", "Encapsulation & interfaces", "Abstraction & patterns", "Extensibility & trade-offs", "Edge cases & testability", "Quality of explanation"].map((c) => (
              <li key={c} className="flex items-start gap-2 bg-slate-50 border border-slate-200 rounded-lg px-3 py-2">
                <span aria-hidden="true" className="text-green-700 font-bold">✓</span>
                <span>{c}</span>
              </li>
            ))}
          </ul>
        </div>
      </section>
    </div>
  );
}
