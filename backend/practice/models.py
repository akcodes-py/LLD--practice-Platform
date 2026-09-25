"""Domain models: Problem, Attempt, Evaluation.

Responsibilities:
- Problem: immutable practice prompt (requirements, constraints, edge cases).
- Attempt: one learner submission draft; owns the design content fields.
- Evaluation: result of running an evaluator against a submitted Attempt.
  Kept separate so a failed evaluation never destroys the submission, and so
  the evaluation provider can vary (rule-based today, LLM/human later).

State model:
  Attempt.status: draft -> submitted -> evaluating -> completed | failed
  Evaluation.state mirrors the terminal part: submitted/evaluating/completed/failed
"""
import uuid

from django.db import models


class Problem(models.Model):
    slug = models.SlugField(max_length=80, unique=True)
    title = models.CharField(max_length=160)
    summary = models.CharField(max_length=280)
    difficulty = models.CharField(
        max_length=16,
        choices=[("beginner", "Beginner"), ("intermediate", "Intermediate"), ("advanced", "Advanced")],
        default="intermediate",
    )
    tags = models.JSONField(default=list, blank=True)
    estimated_minutes = models.PositiveIntegerField(default=45)
    description = models.TextField()
    functional_requirements = models.JSONField(default=list, blank=True)
    constraints = models.JSONField(default=list, blank=True)
    design_considerations = models.JSONField(default=list, blank=True)
    edge_cases = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["title"]

    def __str__(self) -> str:  # pragma: no cover
        return self.title


class Attempt(models.Model):
    STATUS_DRAFT = "draft"
    STATUS_SUBMITTED = "submitted"
    STATUS_EVALUATING = "evaluating"
    STATUS_COMPLETED = "completed"
    STATUS_FAILED = "failed"
    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_SUBMITTED, "Submitted"),
        (STATUS_EVALUATING, "Evaluating"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_FAILED, "Failed"),
    ]
    TERMINAL_STATUSES = {STATUS_COMPLETED, STATUS_FAILED}

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name="attempts")
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_DRAFT)

    # Structured text-based design submission (MVP format).
    requirements_assumptions = models.TextField(blank=True, default="")
    classes_responsibilities = models.TextField(blank=True, default="")
    relationships_interfaces = models.TextField(blank=True, default="")
    workflows = models.TextField(blank=True, default="")
    tradeoffs = models.TextField(blank=True, default="")
    edge_cases = models.TextField(blank=True, default="")

    idempotency_key = models.CharField(max_length=80, blank=True, null=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    submitted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.problem.slug} attempt {self.id}"

    @property
    def content_fields(self) -> dict:
        return {
            "requirements_assumptions": self.requirements_assumptions,
            "classes_responsibilities": self.classes_responsibilities,
            "relationships_interfaces": self.relationships_interfaces,
            "workflows": self.workflows,
            "tradeoffs": self.tradeoffs,
            "edge_cases": self.edge_cases,
        }


class Evaluation(models.Model):
    STATE_SUBMITTED = "submitted"
    STATE_EVALUATING = "evaluating"
    STATE_COMPLETED = "completed"
    STATE_FAILED = "failed"
    STATE_CHOICES = [
        (STATE_SUBMITTED, "Submitted"),
        (STATE_EVALUATING, "Evaluating"),
        (STATE_COMPLETED, "Completed"),
        (STATE_FAILED, "Failed"),
    ]

    PROVIDER_RULE_BASED = "rule_based"
    PROVIDER_LLM = "llm"
    PROVIDER_CHOICES = [
        (PROVIDER_RULE_BASED, "Rule based"),
        (PROVIDER_LLM, "LLM"),
    ]

    attempt = models.OneToOneField(Attempt, on_delete=models.CASCADE, related_name="evaluation")
    state = models.CharField(max_length=16, choices=STATE_CHOICES, default=STATE_SUBMITTED)
    provider = models.CharField(max_length=16, choices=PROVIDER_CHOICES, default=PROVIDER_RULE_BASED)
    total_score = models.FloatField(blank=True, null=True)
    rubric_results = models.JSONField(default=list, blank=True)
    overall_feedback = models.TextField(blank=True, default="")
    strengths = models.JSONField(default=list, blank=True)
    improvements = models.JSONField(default=list, blank=True)
    error = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover
        return f"Evaluation for {self.attempt_id} ({self.state})"
