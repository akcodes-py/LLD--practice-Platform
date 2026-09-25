"""HTTP layer: thin views delegating to services; consistent error envelope."""
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Attempt, Problem
from .serializers import (
    AttemptCreateSerializer,
    AttemptSerializer,
    AttemptUpdateSerializer,
    EvaluationSerializer,
    ProblemDetailSerializer,
    ProblemListSerializer,
)
from .services import CONTENT_FIELDS, ValidationError, retry_attempt, submit_attempt, validate_content


def error_response(code: str, message: str, details=None, http_status=400):
    return Response(
        {"error": {"code": code, "message": message, "details": details or {}}},
        status=http_status,
    )


@api_view(["GET"])
def problem_list(_request):
    problems = Problem.objects.all()
    return Response(ProblemListSerializer(problems, many=True).data)


@api_view(["GET"])
def problem_detail(_request, slug):
    problem = get_object_or_404(Problem, slug=slug)
    return Response(ProblemDetailSerializer(problem).data)


@api_view(["GET", "POST"])
def attempt_list_create(request):
    if request.method == "GET":
        attempts = Attempt.objects.select_related("problem").prefetch_related().all().order_by("-created_at")
        problem_slug = request.query_params.get("problem")
        status_filter = request.query_params.get("status")
        if problem_slug:
            attempts = attempts.filter(problem__slug=problem_slug)
        if status_filter:
            attempts = attempts.filter(status=status_filter)
        return Response(AttemptSerializer(attempts, many=True).data)

    serializer = AttemptCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return error_response("validation_error", "Could not create attempt.", serializer.errors, 400)
    data = serializer.validated_data
    problem = get_object_or_404(Problem, slug=data["problem_slug"])
    idem = data.get("idempotency_key") or None
    if idem:
        existing = Attempt.objects.filter(idempotency_key=idem).first()
        if existing:  # duplicate-safe: return the original instead of creating another
            return Response(AttemptSerializer(existing).data, status=status.HTTP_200_OK)
    try:
        attempt = Attempt.objects.create(
            problem=problem,
            idempotency_key=idem,
            **{f: data.get(f, "") for f in CONTENT_FIELDS},
        )
    except IntegrityError:
        existing = Attempt.objects.filter(idempotency_key=idem).first()
        return Response(AttemptSerializer(existing).data, status=status.HTTP_200_OK)
    return Response(AttemptSerializer(attempt).data, status=status.HTTP_201_CREATED)


@api_view(["GET", "PATCH"])
def attempt_detail(request, attempt_id):
    attempt = get_object_or_404(Attempt.objects.select_related("problem"), id=attempt_id)
    if request.method == "GET":
        return Response(AttemptSerializer(attempt).data)
    # PATCH: drafts only
    if attempt.status != Attempt.STATUS_DRAFT:
        return error_response(
            "not_editable",
            f"Only draft attempts can be edited (current status: {attempt.status}). Use Retry for a new draft.",
            http_status=409,
        )
    serializer = AttemptUpdateSerializer(data=request.data)
    if not serializer.is_valid():
        return error_response("validation_error", "Could not update attempt.", serializer.errors, 400)
    for field, value in serializer.validated_data.items():
        setattr(attempt, field, value)
    attempt.save()
    return Response(AttemptSerializer(attempt).data)


@api_view(["POST"])
def attempt_submit(request, attempt_id):
    attempt = get_object_or_404(Attempt.objects.select_related("problem"), id=attempt_id)
    use_llm = str(request.data.get("use_llm", "")).lower() in ("1", "true", "yes")
    idem = request.data.get("idempotency_key") or None
    # If the client retries the same submit request, return current state (no duplicate processing).
    if idem and attempt.idempotency_key and attempt.idempotency_key == idem and attempt.status in (
        Attempt.STATUS_SUBMITTED, Attempt.STATUS_EVALUATING, Attempt.STATUS_COMPLETED, Attempt.STATUS_FAILED,
    ):
        return Response(AttemptSerializer(attempt).data)
    try:
        evaluation = submit_attempt(attempt, use_llm=use_llm)
    except ValidationError as exc:
        return error_response("validation_error", "Submission needs more detail before evaluation.", exc.errors, 400)
    except ValueError as exc:
        msg = str(exc)
        if "already" in msg.lower():
            return error_response("conflict", msg, http_status=409)
        if "not configured" in msg.lower():
            return error_response("llm_not_configured", msg, http_status=400)
        return error_response("bad_request", msg, http_status=400)
    # Evaluation is now async: return immediately with status=evaluating so the
    # frontend can poll /api/attempts/<id>/status/ until completed/failed.
    attempt.refresh_from_db()
    payload = AttemptSerializer(attempt).data
    payload["evaluation"] = EvaluationSerializer(evaluation).data
    return Response(payload, status=status.HTTP_202_ACCEPTED)


@api_view(["GET"])
def attempt_status(request, attempt_id):
    """Lightweight polling endpoint: returns attempt status + evaluation when ready.

    Frontend polls this every 1-2 s after submit until status is completed or failed.
    Returns 200 in all cases so the client can always read the body.
    """
    attempt = get_object_or_404(
        Attempt.objects.select_related("problem").prefetch_related("evaluation"),
        id=attempt_id,
    )
    return Response(AttemptSerializer(attempt).data)


@api_view(["POST"])
def attempt_retry(request, attempt_id):
    attempt = get_object_or_404(Attempt.objects.select_related("problem"), id=attempt_id)
    if attempt.status == Attempt.STATUS_DRAFT:
        return error_response("bad_request", "This attempt is still a draft; keep editing it instead of retrying.", http_status=400)
    new_attempt = retry_attempt(attempt)
    return Response(AttemptSerializer(new_attempt).data, status=status.HTTP_201_CREATED)


@api_view(["POST"])
def attempt_reevaluate(request, attempt_id):
    attempt = get_object_or_404(Attempt.objects.select_related("problem"), id=attempt_id)
    evaluation = getattr(attempt, "evaluation", None)
    if evaluation is None or evaluation.state != "failed":
        return error_response(
            "not_failed",
            "Only failed evaluations can be re-evaluated. Completed attempts should use Retry for a new attempt.",
            http_status=409,
        )
    # Reset to draft so submit_attempt validation + lifecycle applies cleanly.
    attempt.status = Attempt.STATUS_DRAFT
    attempt.save(update_fields=["status", "updated_at"])
    use_llm = str(request.data.get("use_llm", "")).lower() in ("1", "true", "yes")
    try:
        new_evaluation = submit_attempt(attempt, use_llm=use_llm)
    except ValidationError as exc:
        return error_response("validation_error", "Submission needs more detail before evaluation.", exc.errors, 400)
    except ValueError as exc:
        return error_response("conflict", str(exc), http_status=409)
    # Async: return immediately with evaluating state; frontend polls status.
    attempt.refresh_from_db()
    payload = AttemptSerializer(attempt).data
    payload["evaluation"] = EvaluationSerializer(new_evaluation).data
    return Response(payload, status=status.HTTP_202_ACCEPTED)
