from django.contrib import admin
from django.http import JsonResponse
from django.urls import path, include
from django.views.generic import RedirectView

def root(request):
    return JsonResponse({"rutaviva": "backend running", "docs": "/api/"})

urlpatterns = [
    path("", root),
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),
]

