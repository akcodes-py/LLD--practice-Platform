import { usePageMeta } from "../lib/meta";

export function Privacy() {
  usePageMeta("Privacy policy — LLD Practice Platform", "How this local prototype handles your design submissions.");
  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold tracking-tight">Privacy policy</h1>
      <p className="text-sm text-ink-500 mt-1">Prototype policy, updated {new Date().getFullYear()}.</p>
      <div className="mt-4 space-y-4 text-sm leading-relaxed">
        <p>This prototype runs locally for coursework evaluation. There are no accounts, no tracking cookies, and no analytics.</p>
        <h2 className="font-bold">What is stored</h2>
        <ul className="list-disc pl-5 space-y-1">
          <li>Your design text (the six submission sections) and evaluation results in the backend database (SQLite locally, PostgreSQL in Docker).</li>
          <li>No names, emails, or passwords are collected — the product has no authentication by design.</li>
        </ul>
        <h2 className="font-bold">What is not collected</h2>
        <ul className="list-disc pl-5 space-y-1">
          <li>No non-essential cookies, no advertising identifiers, no analytics beacons. That is why there is no cookie-consent banner: there is nothing to consent to.</li>
          <li>Draft auto-save only talks to your own backend over HTTP on localhost.</li>
        </ul>
        <h2 className="font-bold">AI evaluation</h2>
        <p>The default evaluator is fully local and deterministic. If an operator enables the optional LLM path with their own key, submission text would be sent to that provider; the UI always labels which provider produced each review.</p>
        <h2 className="font-bold">Data removal</h2>
        <p>Delete the backend database file (db.sqlite3) or the Postgres volume to remove all local data.</p>
      </div>
    </div>
  );
}

export function Terms() {
  usePageMeta("Terms of use — LLD Practice Platform", "Prototype terms: educational use, no warranties, your content stays yours.");
  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold tracking-tight">Terms of use</h1>
      <p className="text-sm text-ink-500 mt-1">Prototype terms, updated {new Date().getFullYear()}.</p>
      <div className="mt-4 space-y-4 text-sm leading-relaxed">
        <p>This is an educational prototype built for a 2-day engineering assignment. It is provided “as is”, without warranties.</p>
        <ul className="list-disc pl-5 space-y-1">
          <li>Your designs remain yours. Do not paste secrets, credentials, or personal data into submissions.</li>
          <li>Rule-based feedback is heuristic guidance, not a hiring decision or certification.</li>
          <li>No accounts, payments, or guarantees of availability are offered.</li>
        </ul>
      </div>
    </div>
  );
}

export function NotFound() {
  usePageMeta("Page not found — LLD Practice Platform", "The page you asked for does not exist.");
  return (
    <div className="max-w-xl mx-auto px-4 py-16 text-center">
      <p className="font-mono text-sm text-ink-500">404</p>
      <h1 className="mt-2 text-2xl font-bold">This page slipped out of scope</h1>
      <p className="mt-2 text-sm text-ink-600">The link may be wrong, or the page moved. Your drafts are safe — head back to practice.</p>
      <div className="mt-6 flex justify-center gap-3">
        <a href="/problems" className="btn-primary">Browse problems</a>
        <a href="/" className="btn-secondary">Home</a>
      </div>
    </div>
  );
}
