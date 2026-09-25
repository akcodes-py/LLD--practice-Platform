from rest_framework import serializers

from .models import Attempt, Evaluation, Problem
from .services import CONTENT_FIELDS


class ProblemListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Problem
        fields = ["slug", "title", "summary", "difficulty", "tags", "estimated_minutes"]


class ProblemDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Problem
        fields = [
            "slug", "title", "summary", "difficulty", "tags", "estimated_minutes",
            "description", "functional_requirements", "constraints",
            "design_considerations", "edge_cases",
        ]


class EvaluationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evaluation
        fields = [
            "state", "provider", "total_score", "rubric_results",
            "overall_feedback", "strengths", "improvements", "error",
            "created_at", "completed_at",
        ]


class AttemptSerializer(serializers.ModelSerializer):
    problem_slug = serializers.SlugField(source="problem.slug", read_only=True)
    problem_title = serializers.CharField(source="problem.title", read_only=True)
    evaluation = EvaluationSerializer(read_only=True)

    class Meta:
        model = Attempt
        fields = [
            "id", "problem", "problem_slug", "problem_title", "status",
            *CONTENT_FIELDS,
            "idempotency_key", "created_at", "updated_at", "submitted_at",
            "evaluation",
        ]
        read_only_fields = ["id", "status", "created_at", "updated_at", "submitted_at", "evaluation"]
        extra_kwargs = {"problem": {"required": False}}


class AttemptCreateSerializer(serializers.Serializer):
    problem_slug = serializers.SlugField()
    idempotency_key = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=80)
    requirements_assumptions = serializers.CharField(required=False, allow_blank=True, default="")
    classes_responsibilities = serializers.CharField(required=False, allow_blank=True, default="")
    relationships_interfaces = serializers.CharField(required=False, allow_blank=True, default="")
    workflows = serializers.CharField(required=False, allow_blank=True, default="")
    tradeoffs = serializers.CharField(required=False, allow_blank=True, default="")
    edge_cases = serializers.CharField(required=False, allow_blank=True, default="")


class AttemptUpdateSerializer(serializers.Serializer):
    requirements_assumptions = serializers.CharField(required=False, allow_blank=True)
    classes_responsibilities = serializers.CharField(required=False, allow_blank=True)
    relationships_interfaces = serializers.CharField(required=False, allow_blank=True)
    workflows = serializers.CharField(required=False, allow_blank=True)
    tradeoffs = serializers.CharField(required=False, allow_blank=True)
    edge_cases = serializers.CharField(required=False, allow_blank=True)
