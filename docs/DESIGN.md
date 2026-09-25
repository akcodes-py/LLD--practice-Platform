# Design note — LLD Practice Platform MVP

## 1. MVP scope & user flow

**Scope:** 5 problems, one text-submission format, one evaluation flow (rule-based default + optional LLM),
feedback, history, retry. No auth, payments, LMS, or diagram editors.

**User flow (every step works in the UI):**

```
Home (CTA: Start practicing)
  → /problems (choose)
    → /problems/:slug (read brief: requirements, constraints, considerations, edge cases)
      → Start attempt → /attempts/:id (draft editor, auto-save, validation, honeypot)
        → Submit → /attempts/:id/review (status → rubric feedback)
          → history (/history + per-problem list) → Retry (new draft, old attempts kept)
```

Failure branches: validation errors stay in the editor with per-field messages; evaluator failure shows the error,
keeps the submission, and offers re-evaluation; editing non-drafts is rejected with guidance to retry.

## 2. Architecture & domain model

Modular Django monolith + React SPA. HTTP views are thin; domain rules live in `practice/services.py`;
evaluators share one contract in `practice/evaluators/base.py`.

| Class | Responsibility | Depends on | Likely to change |
|---|---|---|---|
| `Problem` | Immutable practice prompt (brief content) | nothing | new problems only (seed data) |
| `Attempt` | One learner submission; owns the 6 content fields + `status` | `Problem` | new submission formats (additive fields/adapters) |
| `Evaluation` | Result of one evaluator run against an `Attempt` | `Attempt` | new providers (same JSON contract) |
| `services` | Validation, `submit_attempt`, `retry_attempt` lifecycle | models, evaluators | async execution later |
| `evaluators/rule_based` | Deterministic heuristic scoring with quoted evidence | `base.validate_result` | tuning heuristics |
| `evaluators/llm` | Optional LLM scoring, schema-validated | `base.validate_result`, provider API | model/prompt versioning |

No extra patterns were added to “show knowledge”: no repository/UoW layers over Django ORM, no event bus, no
microservices. Each class answers: owns one thing, behaviour lives with data, dependencies point at contracts
(`base.validate_result`), and the two change tests below pass.

## 3. Evaluation & feedback design

- **Rubric (fixed, 8 criteria):** requirement understanding; class responsibilities & cohesion; coupling & dependency
  management; encapsulation & interfaces; abstraction & pattern appropriateness; extensibility & trade-offs; edge cases
  & testability; quality of explanation.
- **Result shape:** `provider, total_score (avg×10), rubric_results[{criterion, score 0–10, evidence, concern,
  suggestion, confidence 0–1}], overall_feedback, strengths[], improvements[]`.
- **Deterministic vs LLM:** field presence/minimum lengths, state transitions, idempotency, and structural heuristics
  are deterministic. The LLM is used only for design reasoning, only when `LLM_ENABLED=1` with a key, with
  JSON-schema validation, timeout, and provider errors surfaced as `failed` — never fabricated. The UI always shows
  “Rule-based review” vs “AI review”.
- **No reference-solution matching:** the rule-based scorer checks explicitness (length, design vocabulary,
  requirement-keyword coverage, trade-off/edge-case reasoning) and quotes the learner’s own text as evidence.

## 4. State transitions & failure handling

```
Attempt: draft ──submit──▶ evaluating ──▶ completed
                                      ╲──▶ failed ──re-evaluate──▶ (evaluating→completed)
Evaluation mirrors: evaluating → completed | failed (with error text)
```

- Submission row is written and status set to evaluating **atomically** before the background thread starts — a crash cannot lose the submission.
- The submit endpoint returns **202 Accepted** immediately; callers poll /api/attempts/<id>/status/ (GET) until completed or ailed.
- Duplicate processing is prevented: evaluating/completed attempts reject re-submit (409, "use Retry"); identical
  `idempotency_key` create/submit returns the existing record.
- Failed evaluations preserve content and error text; `re-evaluate` retries async; `retry` always mints
  a **new** draft so history is append-only.

## 5. Trade-offs & extension points

- **Async evaluation via daemon thread + polling** instead of sync or a full queue: evaluation runs in a background thread, the request returns 202 immediately, and the frontend polls /api/attempts/<id>/status/. No Celery/Redis/broker needed. Next scale step: a persistent EvaluationJob table polled by a worker process — still a monolith, still no Kafka/K8s.  the practice flow is untouched.

