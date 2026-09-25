"""Shared rubric + result contracts for all evaluators.

Every evaluator (rule-based, LLM, future human-review adapter) must return a
dict shaped as:
{
  "provider": "rule_based" | "llm",
  "total_score": float 0..100,
  "rubric_results": [ {criterion, score(0..10), evidence, concern, suggestion, confidence(0..1)} ],
  "overall_feedback": str,
  "strengths": [str],
  "improvements": [str],
}

Change test B (add another evaluator later) only requires implementing this
contract and selecting it in services.run_evaluation.
"""
from dataclasses import dataclass

RUBRIC_CRITERIA = [
    {
        "key": "requirement_understanding",
        "label": "Requirement understanding",
        "description": "Covers the stated functional requirements and names assumptions explicitly.",
    },
    {
        "key": "class_responsibilities",
        "label": "Class responsibilities and cohesion",
        "description": "Each class has one clear job; no god objects; responsibilities are stated.",
    },
    {
        "key": "coupling",
        "label": "Coupling and dependency management",
        "description": "Dependencies point the right way; abstractions reduce direct coupling.",
    },
    {
        "key": "encapsulation",
        "label": "Encapsulation and interfaces",
        "description": "Public contracts are explicit; internals are hidden behind interfaces.",
    },
    {
        "key": "abstraction",
        "label": "Abstraction and pattern appropriateness",
        "description": "Patterns (Strategy, Factory, Observer, State...) used where they fit, not forced.",
    },
    {
        "key": "extensibility",
        "label": "Extensibility and trade-offs",
        "description": "Design can absorb a new requirement; trade-offs are reasoned, not ignored.",
    },
    {
        "key": "edge_cases",
        "label": "Edge cases and testability",
        "description": "Failure modes, concurrency, and testing approach are considered.",
    },
    {
        "key": "explanation",
        "label": "Quality of explanation",
        "description": "A reviewer can follow the reasoning without guessing.",
    },
]

VALID_PROVIDERS = {"rule_based", "llm"}


@dataclass
class EvaluationError(Exception):
    message: str


def validate_result(payload: dict) -> dict:
    """Validate an evaluator result against the contract; raise EvaluationError."""
    if not isinstance(payload, dict):
        raise EvaluationError("Evaluator result must be an object.")
    provider = payload.get("provider")
    if provider not in VALID_PROVIDERS:
        raise EvaluationError(f"Unknown provider: {provider!r}.")
    results = payload.get("rubric_results")
    if not isinstance(results, list) or len(results) != len(RUBRIC_CRITERIA):
        raise EvaluationError(f"rubric_results must list all {len(RUBRIC_CRITERIA)} criteria.")
    expected = [c["key"] for c in RUBRIC_CRITERIA]
    seen = []
    for item in results:
        if not isinstance(item, dict):
            raise EvaluationError("Each rubric result must be an object.")
        for field in ("criterion", "score", "evidence", "concern", "suggestion", "confidence"):
            if field not in item:
                raise EvaluationError(f"Rubric item missing field: {field}.")
        if item["criterion"] not in expected:
            raise EvaluationError(f"Unknown criterion: {item['criterion']!r}.")
        try:
            score = float(item["score"])
        except (TypeError, ValueError):
            raise EvaluationError(f"Score must be numeric for {item['criterion']}.")
        if not 0 <= score <= 10:
            raise EvaluationError(f"Score out of range 0..10 for {item['criterion']}.")
        try:
            conf = float(item["confidence"])
        except (TypeError, ValueError):
            raise EvaluationError(f"Confidence must be numeric for {item['criterion']}.")
        if not 0 <= conf <= 1:
            raise EvaluationError(f"Confidence out of range 0..1 for {item['criterion']}.")
        for text_field in ("evidence", "concern", "suggestion"):
            if not isinstance(item[text_field], str) or not item[text_field].strip():
                raise EvaluationError(f"{text_field} must be a non-empty string for {item['criterion']}.")
        seen.append(item["criterion"])
    if sorted(seen) != sorted(expected):
        raise EvaluationError("rubric_results must cover each criterion exactly once.")
    total = payload.get("total_score")
    try:
        total_f = float(total)
    except (TypeError, ValueError):
        raise EvaluationError("total_score must be numeric.")
    if not 0 <= total_f <= 100:
        raise EvaluationError("total_score must be within 0..100.")
    for field in ("overall_feedback",):
        if not isinstance(payload.get(field), str) or not payload[field].strip():
            raise EvaluationError(f"{field} must be a non-empty string.")
    for field in ("strengths", "improvements"):
        if not isinstance(payload.get(field), list):
            raise EvaluationError(f"{field} must be a list.")
    return payload
