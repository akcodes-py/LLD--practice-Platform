"""Application services: validation + submission lifecycle.

Keeps HTTP views thin and domain rules in one place. Persistence always
happens before evaluation so a failed evaluation never loses the submission.

Async design: submit_attempt persists the submission synchronously, then
spawns a daemon thread to run the evaluator. The request returns immediately
with status=evaluating; callers poll /api/attempts/<id>/status/ until
status transitions to completed or failed.
"""
from __future__ import annotations

import threading

from django.conf import settings
from django.db import connection, transaction
from django.utils import timezone

from .evaluators.base import EvaluationError
from .evaluators.llm import evaluate_with_llm
from .evaluators.rule_based import evaluate_rule_based
from .models import Attempt, Evaluation

CONTENT_FIELDS = [
    "requirements_assumptions",
    "classes_responsibilities",
    "relationships_interfaces",
    "workflows",
    "tradeoffs",
    "edge_cases",
]

FIELD_LABELS = {
    "requirements_assumptions": "Requirements & assumptions",
    "classes_responsibilities": "Classes & responsibilities",
    "relationships_interfaces": "Relationships & interfaces",
    "workflows": "Workflows",
    "tradeoffs": "Trade-offs",
    "edge_cases": "Edge cases",
}

MIN_LENGTHS = {
    "requirements_assumptions": 40,
    "classes_responsibilities": 60,
    "relationships_interfaces": 30,
    "workflows": 30,
    "tradeoffs": 30,
    "edge_cases": 30,
}

# Simulated failure hook for tests: submit with edge_cases containing this
# token to exercise the failure path without external dependencies.
FAILURE_TOKEN = "__simulate_evaluator_failure__"


def validate_content(data: dict) -> dict:
    """Deterministic required-field validation. Returns {field: [messages]}."""
    errors: dict[str, list[str]] = {}
    for field in CONTENT_FIELDS:
        value = str(data.get(field, "") or "").strip()
        if not value:
            errors[field] = [f"{FIELD_LABELS[field]} is required."]
        elif len(value) < MIN_LENGTHS[field]:
            errors[field] = [
                f"{FIELD_LABELS[field]} needs at least {MIN_LENGTHS[field]} characters "
                f"(currently {len(value)}). Add one more concrete sentence."
            ]
    return errors


def _problem_dict(attempt: Attempt) -> dict:
    p = attempt.problem
    return {
        "slug": p.slug,
        "title": p.title,
        "functional_requirements": p.functional_requirements or [],
    }


def _run_evaluator(attempt: Attempt, use_llm: bool = False) -> dict:
    content = {f: getattr(attempt, f) or "" for f in CONTENT_FIELDS}
    if FAILURE_TOKEN in (content.get("edge_cases") or ""):
        raise EvaluationError("Simulated evaluator failure (test hook).")
    if use_llm:
        return evaluate_with_llm(content, _problem_dict(attempt))
    return evaluate_rule_based(content, _problem_dict(attempt))


import time
from django.db.utils import OperationalError


def _run_evaluation_in_background(attempt_id, use_llm: bool) -> None:
    """Worker function executed in a daemon thread.

    Fetches the attempt fresh (own DB connection), runs the evaluator, and
    persists the result. Closes the thread-local DB connection on exit so
    Django's connection pool stays clean.
    """
    try:
        attempt = None
        for attempt_idx in range(10):
            try:
                attempt = Attempt.objects.select_related("problem").get(id=attempt_id)
                break
            except (OperationalError, Attempt.DoesNotExist, RuntimeError):
                if attempt_idx == 9:
                    return
                time.sleep(0.05)

        if not attempt:
            return

        evaluation = attempt.evaluation
        try:
            result = _run_evaluator(attempt, use_llm=use_llm)
        except EvaluationError as exc:
            for save_idx in range(5):
                try:
                    attempt.status = Attempt.STATUS_FAILED
                    attempt.save(update_fields=["status", "updated_at"])
                    evaluation.state = Evaluation.STATE_FAILED
                    evaluation.error = exc.message
                    evaluation.completed_at = timezone.now()
                    evaluation.save(update_fields=["state", "error", "completed_at"])
                    break
                except (OperationalError, RuntimeError):
                    if save_idx == 4:
                        return
                    time.sleep(0.05)
            return
        except RuntimeError:
            return
        except Exception as exc:  # pragma: no cover - defensive
            for save_idx in range(5):
                try:
                    attempt.status = Attempt.STATUS_FAILED
                    attempt.save(update_fields=["status", "updated_at"])
                    evaluation.state = Evaluation.STATE_FAILED
                    evaluation.error = f"Unexpected evaluator error: {exc}"
                    evaluation.completed_at = timezone.now()
                    evaluation.save(update_fields=["state", "error", "completed_at"])
                    break
                except (OperationalError, RuntimeError):
                    if save_idx == 4:
                        return
                    time.sleep(0.05)
            return

        for save_idx in range(5):
            try:
                attempt.status = Attempt.STATUS_COMPLETED
                attempt.save(update_fields=["status", "updated_at"])
                evaluation.state = Evaluation.STATE_COMPLETED
                evaluation.provider = result["provider"]
                evaluation.total_score = result["total_score"]
                evaluation.rubric_results = result["rubric_results"]
                evaluation.overall_feedback = result["overall_feedback"]
                evaluation.strengths = result.get("strengths", [])
                evaluation.improvements = result.get("improvements", [])
                evaluation.error = ""
                evaluation.completed_at = timezone.now()
                evaluation.save()
                break
            except (OperationalError, RuntimeError):
                if save_idx == 4:
                    return
                time.sleep(0.05)
    except RuntimeError:
        return
    finally:
        try:
            # Always release the thread-local DB connection back to the pool.
            connection.close()
        except Exception:
            pass


def submit_attempt(attempt: Attempt, use_llm: bool = False) -> Evaluation:
    """Persist submission and kick off async evaluation. Returns immediately.

    The submission row is written synchronously before the background thread
    starts, so a crash during evaluation can never lose the learner's content.
    Callers poll /api/attempts/<id>/status/ until status is completed or failed.
    """
    if attempt.status in (Attempt.STATUS_SUBMITTED, Attempt.STATUS_EVALUATING):
        raise ValueError("This attempt is already being evaluated.")
    if attempt.status == Attempt.STATUS_COMPLETED:
        raise ValueError("This attempt is already completed. Use Retry to create a new attempt.")
    errors = validate_content(attempt.content_fields)
    if errors:
        raise ValidationError(errors)

    requested_llm = bool(use_llm)
    if requested_llm and not (settings.LLM_ENABLED and settings.LLM_API_KEY):
        raise ValueError("AI evaluation is not configured on this server. Your draft is saved; rule-based review is available.")

    # Phase 1 (synchronous): persist the submission and evaluation row before
    # anything async happens. A crash between here and the thread start cannot
    # lose the submission — the row is in the DB with status=evaluating.
    with transaction.atomic():
        attempt.status = Attempt.STATUS_EVALUATING
        attempt.submitted_at = timezone.now()
        attempt.save(update_fields=["status", "submitted_at", "updated_at"])
        evaluation, _ = Evaluation.objects.get_or_create(
            attempt=attempt,
            defaults={"state": Evaluation.STATE_EVALUATING},
        )
        # Re-submission after failure reuses the same row (no duplicate evaluations).
        evaluation.state = Evaluation.STATE_EVALUATING
        evaluation.error = ""
        evaluation.provider = Evaluation.PROVIDER_LLM if requested_llm else Evaluation.PROVIDER_RULE_BASED
        evaluation.save()

    # Phase 2 (async): run the evaluator in a daemon background thread.
    # The thread fetches a fresh queryset with its own DB connection.
    t = threading.Thread(
        target=_run_evaluation_in_background,
        args=(attempt.id, requested_llm),
        daemon=True,
        name=f"eval-{attempt.id}",
    )
    t.start()

    return evaluation


def retry_attempt(attempt: Attempt) -> Attempt:
    """Create a fresh draft cloning content; history is preserved."""
    return Attempt.objects.create(
        problem=attempt.problem,
        status=Attempt.STATUS_DRAFT,
        **attempt.content_fields,
    )


class ValidationError(Exception):
    def __init__(self, errors: dict):
        super().__init__("Validation failed")
        self.errors = errors
