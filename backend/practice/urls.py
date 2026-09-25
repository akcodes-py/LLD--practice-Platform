from django.urls import path

from . import views

urlpatterns = [
    path("problems/", views.problem_list, name="problem-list"),
    path("problems/<slug:slug>/", views.problem_detail, name="problem-detail"),
    path("attempts/", views.attempt_list_create, name="attempt-list-create"),
    path("attempts/<uuid:attempt_id>/", views.attempt_detail, name="attempt-detail"),
    path("attempts/<uuid:attempt_id>/status/", views.attempt_status, name="attempt-status"),
    path("attempts/<uuid:attempt_id>/submit/", views.attempt_submit, name="attempt-submit"),
    path("attempts/<uuid:attempt_id>/retry/", views.attempt_retry, name="attempt-retry"),
    path("attempts/<uuid:attempt_id>/re-evaluate/", views.attempt_reevaluate, name="attempt-reevaluate"),
]
