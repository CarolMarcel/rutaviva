from django.urls import path
from .views import (me, register, login_jwt, eventos_list, evento_crud_admin, crear_reserva, aprobar_rechazar_reserva, confirmar_reserva,
    reservas_admin, blacklist_toggle, asignacion_upsert, health, mis_reservas, cancelar_reserva, TourListView, TourDetailView)

urlpatterns = [
    path("health/", health),

    # Salud y auth...
    path("api/tours/", TourListView.as_view(), name="tours-list"),
    path("api/tours/<int:pk>/", TourDetailView.as_view(), name="tours-detail"),

    # auth
    path("auth/register/", register),
    path("auth/login/", login_jwt),
    path("auth/me/", me),

    # eventos
    path("eventos/", eventos_list),
    path("eventos/<int:evento_id>/", evento_crud_admin),

    # reservas
    path("reservas/", crear_reserva),
    path("reservas/admin/", reservas_admin),
    path("reservas/<int:reserva_id>/aprobar/", aprobar_rechazar_reserva),
    path("reservas/confirmar/<str:token>/", confirmar_reserva),
    path("reservas/mine/", mis_reservas, name="mis_reservas"),   # 👈 nuevo endpoint
    path("reservas/<int:reserva_id>/cancel/", cancelar_reserva, name="cancelar_reserva"),

    # blacklist / asignación
    path("admin/blacklist/<int:user_id>/toggle/", blacklist_toggle),
    path("admin/eventos/<int:evento_id>/asignacion/", asignacion_upsert),
]
