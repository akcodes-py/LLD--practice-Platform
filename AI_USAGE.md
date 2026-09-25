# AI usage

AI (Claude-style assistance) was used as a sounding board during this build. Each decision below was reviewed against
the assignment brief and the actual codebase; several suggestions were rejected or reshaped.

## 1. Submission format: structured text over code/diagram editors

- **Suggested:** support code + diagram uploads from day one for “richer evidence”.
- **Accepted in part / rejected in full:** chose six-section structured text only.
- **Why:** code needs compile/test infra and diagrams need an editor — both double the build without doubling the
  learning signal. The helping guide asks for the *smallest sufficient* format; text captures assumptions,
  responsibilities, interfaces, and trade-offs, which is exactly what the rubric scores. Code/diagram stay documented
  extension points (see architectural change tests in README).

## 2. Evaluation contract: criterion → evidence → concern → suggestion → confidence

- **Suggested:** return per-criterion scores plus an overall 0–100 score with free-text comments.
- **Accepted with changes:** kept that shape but made `evidence` mandatory (quoted from the submission) and added
  `confidence`, plus strict schema validation (`evaluators/base.py`).
- **Why:** a bare score is unactionable and drifts between runs. Requiring quoted evidence forces feedback to point at
  the learner’s actual words and makes rule-based and LLM providers comparable and testable.

## 3. Deterministic default with optional LLM (not AI-first)

- **Suggested:** call an LLM for every evaluation for “deeper feedback”.
- **Rejected as default, accepted as opt-in:** the default is a labelled rule-based evaluator that works offline; the
  LLM path requires `LLM_ENABLED=1` + key, validates the response schema, and surfaces failures honestly.
- **Why:** no key is available in this environment, and pretending otherwise would mean fabricated “AI” responses.
  The brief explicitly rewards separating deterministic checks from judgment and handling provider failure — the
  current design does that, and every review is labelled with its real provider.

## 4. Async evaluation: daemon thread + polling (not a full job queue)

- **Suggested:** add Celery/Redis or a background worker for production readiness.
- **Accepted with changes:** evaluation runs in a daemon background thread; the submit endpoint returns 202 immediately with `status=evaluating`; the frontend polls `/api/attempts/<id>/status/` every 1.5 s until `completed` or `failed`. No external broker.
- **Why:** a full Celery/Redis stack is distributed-systems scope the brief tells candidates not to build. A daemon thread gives the non-blocking user experience (submit then instant redirect then polling spinner then feedback) with zero extra infra. The submission row is persisted atomically before the thread starts, so a thread crash cannot lose content. The DB connection is explicitly closed in a `finally` block so the thread-local pool stays clean. The documented next step is a persistent `EvaluationJob` table plus a dedicated worker process.
## 5. UI restraint over dashboard clichés

- **Suggested (implicit in many templates):** gradient hero, stat cards, decorative charts.
- **Rejected:** built a restrained light theme (white cards, slate borders, single orange primary, Inter/system type),
  one clear CTA, and feedback-first components (score bars, criterion panels, `details` for the submission).
- **Why:** the audit and checklist demand hierarchy, contrast, and mobile usability over decoration. Applied the
  audit’s real tokens (Cipher orange `#F3912E`, Inter, 12px card radius) without copying unrelated course-site
  sections into a practice tool.

