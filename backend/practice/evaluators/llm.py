"""Optional LLM evaluator (only used when explicitly enabled + key present).

Contract: same output shape as rule-based. The response is validated with
base.validate_result; any schema violation, timeout, or provider error raises
EvaluationError so the caller can mark the evaluation Failed honestly instead
of showing fabricated feedback. API keys stay on the backend (never frontend).
"""
from __future__ import annotations

import json

import requests
from django.conf import settings

from .base import RUBRIC_CRITERIA, EvaluationError, validate_result

SYSTEM_PROMPT = (
    "You review low-level designs (classes, responsibilities, interfaces, "
    "trade-offs). There is no single correct solution; acknowledge valid "
    "alternatives. Return ONLY JSON matching the requested schema. Be concise, "
    "cite evidence quoted from the submission, and never invent submission text."
)


def _rubric_spec() -> str:
    lines = [f"- {c['key']}: {c['label']} — {c['description']}" for c in RUBRIC_CRITERIA]
    return "\n".join(lines)


def evaluate_with_llm(content: dict, problem: dict | None = None) -> dict:
    if not settings.LLM_ENABLED:
        raise EvaluationError("LLM evaluator is disabled (LLM_ENABLED=0).")
    if not settings.LLM_API_KEY:
        raise EvaluationError("LLM evaluator needs LLM_API_KEY to be configured.")

    problem_text = ""
    if problem:
        problem_text = (
            f"Problem: {problem.get('title', '')}\n"
            f"Requirements: {'; '.join((problem.get('functional_requirements') or [])[:12])}"
        )
    submission_text = "\n\n".join(f"## {k}\n{v or '(empty)'}" for k, v in content.items())
    user_prompt = (
        f"{problem_text}\n\nSubmission:\n{submission_text}\n\n"
        f"Rubric (score each 0..10):\n{_rubric_spec()}\n\n"
        "Return JSON with keys: provider ('llm'), total_score (0..100), "
        "rubric_results (list of {criterion, score, evidence, concern, suggestion, confidence 0..1} "
        "covering ALL 8 criteria), overall_feedback, strengths (list), improvements (list)."
    )
    try:
        resp = requests.post(
            f"{settings.LLM_BASE_URL.rstrip('/')}/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.LLM_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": settings.LLM_MODEL,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": 0.2,
                "response_format": {"type": "json_object"},
            },
            timeout=settings.LLM_TIMEOUT_SECONDS,
        )
    except requests.RequestException as exc:
        raise EvaluationError(f"LLM provider request failed: {exc}") from exc
    if resp.status_code != 200:
        raise EvaluationError(f"LLM provider returned HTTP {resp.status_code}.")
    try:
        data = resp.json()
        raw = data["choices"][0]["message"]["content"]
        payload = json.loads(raw)
    except (KeyError, IndexError, ValueError, TypeError) as exc:
        raise EvaluationError(f"LLM response was not valid JSON: {exc}") from exc
    payload["provider"] = "llm"
    return validate_result(payload)
