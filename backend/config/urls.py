from django.http import JsonResponse
from django.urls import include, path


def health(_request):
    return JsonResponse({"status": "ok", "service": "lld-practice-platform"})


urlpatterns = [
    path("api/health/", health, name="health"),
    path("api/", include("practice.urls")),
]
