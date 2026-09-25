"""API + domain tests for the practice loop (async evaluation model)."""
import time
import pytest
from django.core.management import call_command

from practice.models import Attempt, Evaluation, Problem
from practice.services import CONTENT_FIELDS

GOOD_CONTENT = {
    "requirements_assumptions": (
        "Assumptions: single mall building, hourly pricing per vehicle type. "
        "Requirement mapping: floors and spot sizes covered by ParkingLot and Floor; "
        "ticketing by Ticket with unique id and timestamps; payment by Payment hierarchy; "
        "availability query by ParkingLot; concurrency handled with a lock on allocation."
    ),
    "classes_responsibilities": (
        "ParkingLot owns floors and delegates allocation to a SpotAllocationStrategy (Strategy pattern) "
        "so nearest-fit can be swapped. Floor owns its spots. Spot holds size and occupancy only. "
        "Vehicle hierarchy (Motorcycle, Car, Bus) knows its size. Ticket is a value record of entry. "
        "Pricing is a separate PriceCalculator (open-closed). Each class has a single responsibility; "
        "no god object. Composition is preferred over inheritance except for vehicle/payment types."
    ),
    "relationships_interfaces": (
        "ParkingLot depends on IAllocationStrategy and IPayment interfaces, not concretes. "
        "Payment is abstract with CashPayment, CardPayment, UPI concrete types (dependency inversion). "
        "Ticket references Spot by id to avoid bidirectional coupling. Public methods: "
        "allocate(vehicle)->Ticket, release(ticket)->Receipt. Internals like spot lists stay private."
    ),
    "workflows": (
        "Entry: vehicle arrives -> find suitable spot via strategy -> create ticket with entry time. "
        "Exit: scan ticket -> compute fee from duration and vehicle type -> collect payment -> release spot. "
        "We chose strategy injection because allocation policy changes independently of the lot."
    ),
    "tradeoffs": (
        "Trade-off: nearest-fit is fast but fragments large spots; we reserve one bus row to bound this. "
        "Alternative considered: per-floor managers; rejected because cross-floor nearest search needs a global view. "
        "Extensibility: EV spots added as a new Spot subtype plus a pricing rule; no core rewrite (open-closed)."
    ),
    "edge_cases": (
        "Edge cases: lot full for cars while bus spots free (reject with clear message, no oversized downgrade). "
        "Concurrent allocation guarded by a lock so the last spot is given once. "
        "Lost ticket verified by plate log. Payment failure keeps the spot held and the barrier closed. "
        "Tested with unit tests for fee math and a concurrency test for double booking."
    ),
}


@pytest.fixture
def problem(db):
    call_command("seed_problems", verbosity=0)
    return Problem.objects.get(slug="parking-lot")


@pytest.fixture
def problem_tx(django_db_blocker):
    """Like `problem` but works with transaction=True tests (transactional_db)."""
    with django_db_blocker.unblock():
        call_command("seed_problems", verbosity=0)
        return Problem.objects.get(slug="parking-lot")


def _draft(problem, **overrides):
    data = {f: "placeholder" for f in CONTENT_FIELDS} | overrides
    return Attempt.objects.create(problem=problem, **data)


def _wait_for_terminal(client, attempt_id, max_wait=5.0, interval=0.1):
    """Poll /api/attempts/<id>/status/ until attempt reaches a terminal status.

    The rule-based evaluator completes in milliseconds in tests, so this
    typically exits after the first or second poll.
    """
    deadline = time.monotonic() + max_wait
    while time.monotonic() < deadline:
        resp = client.get(f"/api/attempts/{attempt_id}/status/")
        body = resp.json()
        if body["status"] in ("completed", "failed"):
            return body
        time.sleep(interval)
    raise AssertionError(f"Attempt {attempt_id} did not reach terminal status within {max_wait}s")


@pytest.mark.django_db
def test_problem_list_and_detail(client, problem):
    resp = client.get("/api/problems/")
    assert resp.status_code == 200
    assert len(resp.json()) == 5
    detail = client.get("/api/problems/parking-lot/")
    assert detail.status_code == 200
    body = detail.json()
    assert len(body["functional_requirements"]) >= 5
    assert body["constraints"] and body["edge_cases"]


@pytest.mark.django_db(transaction=True)
def test_create_edit_submit_full_journey(client, problem_tx):
    problem = problem_tx
    created = client.post("/api/attempts/", {"problem_slug": "parking-lot"}, content_type="application/json")
    assert created.status_code == 201
    attempt_id = created.json()["id"]

    patched = client.patch(
        f"/api/attempts/{attempt_id}/", GOOD_CONTENT, content_type="application/json"
    )
    assert patched.status_code == 200

    # Submit returns 202 immediately with status=evaluating (async evaluation).
    submitted = client.post(f"/api/attempts/{attempt_id}/submit/", {}, content_type="application/json")
    assert submitted.status_code == 202
    assert submitted.json()["status"] == "evaluating"

    # Poll /status/ until the background thread finishes.
    final = _wait_for_terminal(client, attempt_id)
    assert final["status"] == "completed"
    evaluation = final["evaluation"]
    assert evaluation["state"] == "completed"
    assert evaluation["provider"] == "rule_based"
    assert 0 <= evaluation["total_score"] <= 100
    assert len(evaluation["rubric_results"]) == 8
    for item in evaluation["rubric_results"]:
        for field in ("criterion", "score", "evidence", "concern", "suggestion", "confidence"):
            assert field in item

    # History shows the completed attempt.
    history = client.get("/api/attempts/?problem=parking-lot")
    assert history.status_code == 200
    assert any(a["id"] == attempt_id for a in history.json())


@pytest.mark.django_db(transaction=True)
def test_status_endpoint_returns_current_state(client, problem_tx):
    problem = problem_tx
    """Polling endpoint returns 200 and the correct attempt shape at any lifecycle stage."""
    attempt = _draft(problem, **GOOD_CONTENT)
    # Before submit: draft.
    resp = client.get(f"/api/attempts/{attempt.id}/status/")
    assert resp.status_code == 200
    assert resp.json()["status"] == "draft"

    # After submit: poll until terminal.
    client.post(f"/api/attempts/{attempt.id}/submit/", {}, content_type="application/json")
    final = _wait_for_terminal(client, attempt.id)
    assert final["status"] == "completed"
    assert final["evaluation"]["state"] == "completed"


@pytest.mark.django_db
def test_submit_validation_blocks_empty_content(client, problem):
    attempt = _draft(problem)
    resp = client.post(f"/api/attempts/{attempt.id}/submit/", {}, content_type="application/json")
    assert resp.status_code == 400
    body = resp.json()
    assert body["error"]["code"] == "validation_error"
    assert "classes_responsibilities" in body["error"]["details"]
    attempt.refresh_from_db()
    assert attempt.status == "draft"  # never moved to evaluating
    assert not Evaluation.objects.filter(attempt=attempt).exists()


@pytest.mark.django_db(transaction=True)
def test_duplicate_submit_is_rejected_without_duplicate_evaluation(client, problem_tx):
    problem = problem_tx
    attempt = _draft(problem, **GOOD_CONTENT)
    first = client.post(f"/api/attempts/{attempt.id}/submit/", {}, content_type="application/json")
    assert first.status_code == 202
    _wait_for_terminal(client, attempt.id)
    assert Evaluation.objects.filter(attempt=attempt).count() == 1
    second = client.post(f"/api/attempts/{attempt.id}/submit/", {}, content_type="application/json")
    assert second.status_code == 409
    assert Evaluation.objects.filter(attempt=attempt).count() == 1


@pytest.mark.django_db
def test_idempotent_create_with_idempotency_key(client, problem):
    payload = {"problem_slug": "parking-lot", "idempotency_key": "demo-key-123"}
    first = client.post("/api/attempts/", payload, content_type="application/json")
    second = client.post("/api/attempts/", payload, content_type="application/json")
    assert first.status_code == 201
    assert second.status_code == 200
    assert first.json()["id"] == second.json()["id"]


@pytest.mark.django_db(transaction=True)
def test_failed_evaluation_preserves_submission_and_allows_reevaluate(client, problem_tx):
    problem = problem_tx
    bad = dict(GOOD_CONTENT)
    bad["edge_cases"] = "__simulate_evaluator_failure__ " + bad["edge_cases"]
    attempt = _draft(problem, **bad)
    client.post(f"/api/attempts/{attempt.id}/submit/", {}, content_type="application/json")
    final = _wait_for_terminal(client, attempt.id)
    assert final["status"] == "failed"
    assert final["evaluation"]["state"] == "failed"
    assert final["evaluation"]["error"]
    attempt.refresh_from_db()
    assert attempt.classes_responsibilities == GOOD_CONTENT["classes_responsibilities"]  # intact

    # Fix the hook content directly (failed attempts are immutable via API),
    # then re-evaluate the same attempt without losing history.
    Attempt.objects.filter(id=attempt.id).update(status="draft", edge_cases=GOOD_CONTENT["edge_cases"])
    retry = client.post(f"/api/attempts/{attempt.id}/re-evaluate/", {}, content_type="application/json")
    assert retry.status_code == 202
    final2 = _wait_for_terminal(client, attempt.id)
    assert final2["status"] == "completed"


@pytest.mark.django_db(transaction=True)
def test_retry_creates_new_draft_and_preserves_history(client, problem_tx):
    problem = problem_tx
    attempt = _draft(problem, **GOOD_CONTENT)
    client.post(f"/api/attempts/{attempt.id}/submit/", {}, content_type="application/json")
    _wait_for_terminal(client, attempt.id)
    resp = client.post(f"/api/attempts/{attempt.id}/retry/", {}, content_type="application/json")
    assert resp.status_code == 201
    body = resp.json()
    assert body["status"] == "draft"
    assert body["classes_responsibilities"] == GOOD_CONTENT["classes_responsibilities"]
    assert body["id"] != str(attempt.id)
    history = client.get("/api/attempts/?problem=parking-lot").json()
    assert len([a for a in history if a["problem_slug"] == "parking-lot"]) == 2


@pytest.mark.django_db
def test_editing_evaluating_attempt_is_blocked(client, problem):
    """Editing is blocked as soon as status transitions to evaluating (async-safe)."""
    attempt = _draft(problem, **GOOD_CONTENT)
    client.post(f"/api/attempts/{attempt.id}/submit/", {}, content_type="application/json")
    # Status is evaluating immediately after submit returns 202.
    resp = client.patch(
        f"/api/attempts/{attempt.id}/", {"workflows": "changed"}, content_type="application/json"
    )
    assert resp.status_code == 409
