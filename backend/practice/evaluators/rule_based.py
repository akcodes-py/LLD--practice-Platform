"""Deterministic rule-based evaluator (no AI).

It never pretends to be AI-generated. It checks structural evidence:
length, presence of design vocabulary, requirement keyword coverage, and
explicit trade-off / edge-case reasoning. Scores are heuristic but every
item cites evidence quoted from the learner's own submission, and low
scores always carry an actionable suggestion. Alternative valid designs
are acknowledged in the overall feedback text.
"""
import re

from .base import RUBRIC_CRITERIA, validate_result

MIN_FIELD_LENGTHS = {
    "requirements_assumptions": 80,
    "classes_responsibilities": 120,
    "relationships_interfaces": 60,
    "workflows": 60,
    "tradeoffs": 60,
    "edge_cases": 60,
}

DESIGN_VOCAB = {
    "class_responsibilities": ["responsib", "cohesion", "single responsibility", "srp", "god object", "class"],
    "coupling": ["coupling", "dependenc", "inject", "abstraction", "interface", "decouple"],
    "encapsulation": ["encapsulat", "private", "public api", "interface", "contract", "getter", "setter", "hide"],
    "abstraction": ["pattern", "strategy", "factory", "observer", "decorator", "state", "singleton", "abstract", "composition", "inheritance"],
    "extensibility": ["extensib", "open-closed", "open/closed", "trade-off", "tradeoff", "scale", "future", "alternative"],
    "edge_cases": ["edge", "concurren", "thread", "race", "failure", "timeout", "test", "null", "invalid", "capacity"],
    "explanation": ["because", "therefore", "so that", "rationale", "reason"],
}


def _combined_text(content: dict) -> str:
    return "\n".join(str(content.get(k, "") or "") for k in MIN_FIELD_LENGTHS)


def _snippet(text: str, limit: int = 180) -> str:
    one_line = re.sub(r"\s+", " ", text or "").strip()
    if len(one_line) <= limit:
        return one_line or "(empty)"
    return one_line[:limit].rstrip() + "..."


def _field_evidence(content: dict, field: str) -> str:
    value = (content.get(field) or "").strip()
    if not value:
        return "This section was left empty."
    return f'Quoted from "{field}": "{_snippet(value)}"'


def _vocab_hits(text: str, terms: list) -> list:
    lowered = text.lower()
    return [t for t in terms if t.lower() in lowered]


def _score_for(field_len: int, minimum: int, hits: list, expected_hits: int = 2) -> float:
    if field_len <= 0:
        return 1.0
    if field_len < minimum * 0.5:
        base = 3.0
    elif field_len < minimum:
        base = 5.0
    elif field_len < minimum * 2:
        base = 7.0
    else:
        base = 8.0
    if not hits:
        base -= 1.5
    elif len(hits) >= expected_hits:
        base += 1.0
    return round(max(1.0, min(9.5, base)), 1)


def evaluate_rule_based(content: dict, problem: dict | None = None) -> dict:
    full = _combined_text(content)
    full_len = len(full.strip())
    problem_keywords: list = []
    if problem:
        for req in problem.get("functional_requirements", []) or []:
            words = re.findall(r"[A-Za-z]{4,}", str(req))
            problem_keywords.extend(w.lower() for w in words[:6])
    problem_keywords = list(dict.fromkeys(problem_keywords))[:30]

    req_text = content.get("requirements_assumptions", "") or ""
    lowered_req = req_text.lower()
    covered = [k for k in problem_keywords if k in lowered_req] if problem_keywords else []
    coverage = (len(covered) / len(problem_keywords)) if problem_keywords else 0.0

    # Requirement understanding score blends length + keyword coverage.
    if len(req_text.strip()) == 0:
        req_score = 1.0
    else:
        req_score = _score_for(len(req_text.strip()), MIN_FIELD_LENGTHS["requirements_assumptions"], covered, 3)
        if problem_keywords and coverage < 0.2:
            req_score = max(1.0, req_score - 1.5)

    per_criterion_field = {
        "class_responsibilities": "classes_responsibilities",
        "coupling": "relationships_interfaces",
        "encapsulation": "relationships_interfaces",
        "abstraction": "classes_responsibilities",
        "extensibility": "tradeoffs",
        "edge_cases": "edge_cases",
        "explanation": "workflows",
    }

    items = []
    # 1. Requirement understanding
    if req_score >= 7:
        concern = "Minor gaps may remain against less-common requirements."
        suggestion = "Re-read each functional requirement and add one line mapping it to a class or workflow step."
    elif req_score >= 5:
        concern = "Several requirements are restated but not clearly owned by part of the design."
        suggestion = "List each requirement, mark it covered/assumption, and name the class or flow that satisfies it."
    else:
        concern = "The submission does not show which requirements are addressed or what was assumed."
        suggestion = "Write 4-8 bullet assumptions and map every functional requirement to a design element."
    items.append({
        "criterion": "requirement_understanding",
        "score": req_score,
        "evidence": _field_evidence(content, "requirements_assumptions")
        + (f" Keyword coverage: {len(covered)}/{len(problem_keywords)} matched." if problem_keywords else ""),
        "concern": concern,
        "suggestion": suggestion,
        "confidence": 0.8 if full_len > 400 else 0.6,
    })

    for crit in RUBRIC_CRITERIA[1:]:
        key = crit["key"]
        field = per_criterion_field[key]
        text = content.get(field, "") or ""
        vocab = DESIGN_VOCAB.get(key, [])
        # Coupling/encapsulation/abstraction benefit from whole-submission vocabulary too.
        pool = text + "\n" + full if key in ("coupling", "encapsulation", "abstraction", "explanation") else text
        hits = _vocab_hits(pool, vocab)
        score = _score_for(len(text.strip()), MIN_FIELD_LENGTHS[field], hits)
        if score >= 7:
            concern = f"Solid start on {crit['label'].lower()}; depth could grow with a concrete example."
            suggestion = f"Add one concrete before/after or alternative-considered note for {crit['label'].lower()}."
        elif score >= 5:
            concern = f"{crit['label']} is mentioned but the reasoning stays generic."
            suggestion = f"Name the specific classes/interfaces involved and why the choice helps {crit['label'].lower()}."
        else:
            concern = f"Little evidence of {crit['label'].lower()} in the submission."
            suggestion = _suggestion_for(key)
        # Evidence quotes the most relevant section; vocabulary hits make it auditable.
        evidence = _field_evidence(content, field)
        if hits:
            evidence += f" Detected terms: {', '.join(hits[:5])}."
        else:
            evidence += " No core design vocabulary detected in this section."
        items.append({
            "criterion": key,
            "score": score,
            "evidence": evidence,
            "concern": concern,
            "suggestion": suggestion,
            "confidence": 0.75 if len(text.strip()) > 80 else 0.55,
        })

    avg = sum(i["score"] for i in items) / len(items)
    total = round(avg * 10, 1)
    weak = sorted(items, key=lambda i: i["score"])[:2]
    strong = sorted(items, key=lambda i: i["score"], reverse=True)[:2]
    overall = (
        "Rule-based review (deterministic, not AI). "
        "This checks structure and explicit reasoning, not whether your design matches one reference solution — "
        "alternative valid designs can score well when responsibilities, interfaces, and trade-offs are stated clearly. "
        f"Strongest areas: {', '.join(_label(w['criterion']) for w in strong)}. "
        f"Focus next on: {', '.join(_label(w['criterion']) for w in weak)}."
    )
    result = {
        "provider": "rule_based",
        "total_score": total,
        "rubric_results": items,
        "overall_feedback": overall,
        "strengths": [f"{_label(w['criterion'])}: {w['evidence']}" for w in strong],
        "improvements": [f"{_label(w['criterion'])}: {w['suggestion']}" for w in weak],
    }
    return validate_result(result)


def _label(key: str) -> str:
    for c in RUBRIC_CRITERIA:
        if c["key"] == key:
            return c["label"]
    return key


def _suggestion_for(key: str) -> str:
    return {
        "class_responsibilities": "Give each class one sentence: what it owns, what it does not own. Split any class doing two jobs.",
        "coupling": "Draw the dependency arrows: which class knows about which? Replace one concrete dependency with an interface.",
        "encapsulation": "Write the public method signatures for two key classes and mark what stays private.",
        "abstraction": "Name one pattern you used (or deliberately avoided) and one sentence on why it fits here.",
        "extensibility": "Pick one likely change (new vehicle type, new pricing rule) and describe what would and would not change.",
        "edge_cases": "List 3 failure cases (concurrency, invalid input, capacity) and how the design handles or tests each.",
        "explanation": "Add rationale sentences ('we chose X because...') so a reviewer can follow decisions without guessing.",
    }.get(key, "Add a concrete example and one sentence of reasoning.")
