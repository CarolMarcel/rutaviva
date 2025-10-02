# backend/urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import (
    TourViewSet, CulturalEventViewSet, ReservationViewSet,
    register, me, confirm_reservation
)

router = DefaultRouter()
router.register(r'tours', TourViewSet, basename='tour')
router.register(r'events', CulturalEventViewSet, basename='cevent')
router.register(r'reservations', ReservationViewSet, basename='reservation')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/auth/register/', register),
    path('api/auth/me/', me),
    path('api/reservations/confirm/<str:token>/', confirm_reservation),
    path('api/auth/', include('rest_framework_simplejwt.urls')),  # /api/auth/token/ y /api/auth/token/refresh/
]
