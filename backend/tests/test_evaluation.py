"""Unit tests for the deterministic evaluator contract."""
import pytest
from django.core.management import call_command

from practice.evaluators.base import RUBRIC_CRITERIA, validate_result
from practice.evaluators.llm import evaluate_with_llm
from practice.evaluators.rule_based import evaluate_rule_based
from practice.evaluators.base import EvaluationError
from practice.models import Problem
from tests.test_api import GOOD_CONTENT


@pytest.mark.django_db
def test_rule_based_returns_full_rubric_with_evidence():
    call_command("seed_problems", verbosity=0)
    problem = Problem.objects.get(slug="parking-lot")
    result = evaluate_rule_based(
        GOOD_CONTENT,
        {"title": problem.title, "functional_requirements": problem.functional_requirements},
    )
    assert result["provider"] == "rule_based"
    assert len(result["rubric_results"]) == len(RUBRIC_CRITERIA) == 8
    assert 0 <= result["total_score"] <= 100
    for item in result["rubric_results"]:
        assert item["evidence"].strip()
        assert item["suggestion"].strip()


@pytest.mark.django_db
def test_rule_based_penalises_empty_submission():
    call_command("seed_problems", verbosity=0)
    problem = Problem.objects.get(slug="parking-lot")
    empty = {k: "" for k in GOOD_CONTENT}
    result = evaluate_rule_based(
        empty, {"title": problem.title, "functional_requirements": problem.functional_requirements}
    )
    assert result["total_score"] < 30
    assert any("empty" in i["evidence"].lower() for i in result["rubric_results"])


def test_llm_disabled_raises_honest_error():
    with pytest.raises(EvaluationError, match="disabled"):
        evaluate_with_llm(GOOD_CONTENT)


def test_validate_result_rejects_bad_schema():
    with pytest.raises(EvaluationError):
        validate_result({"provider": "rule_based"})
