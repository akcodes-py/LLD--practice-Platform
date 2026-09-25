from django.contrib import admin

from .models import Attempt, Evaluation, Problem


@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ("slug", "title", "difficulty", "estimated_minutes")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ("id", "problem", "status", "created_at")
    list_filter = ("status", "problem")


@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    list_display = ("attempt", "state", "provider", "total_score")
    list_filter = ("state", "provider")
