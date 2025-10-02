import secrets
from datetime import date
from django.db.models import Q
from django.core.mail import send_mail
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Tour, Reservation, CulturalEvent, BlackList
from .serializers import (
    TourSerializer, ReservationSerializer, CulturalEventSerializer,
    RegisterSerializer, UserSerializer
)
from .permissions import IsAdmin, IsStaff

# --- Auth helpers ---
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    ser = RegisterSerializer(data=request.data)
    ser.is_valid(raise_exception=True)
    user = ser.save()
    return Response(UserSerializer(user).data, status=201)

@api_view(['GET'])
def me(request):
    return Response(UserSerializer(request.user).data)


# --- Catálogo Tours público ---
class TourViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tour.objects.filter(is_active=True).order_by('date','time')
    serializer_class = TourSerializer
    permission_classes = [AllowAny]


# --- Cultural events público (opcional en home) ---
class CulturalEventViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CulturalEvent.objects.all().order_by('date')
    serializer_class = CulturalEventSerializer
    permission_classes = [AllowAny]


# --- Reservas del cliente ---
class ReservationViewSet(viewsets.ModelViewSet):
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        u = self.request.user
        # admin/staff ven todas | cliente solo las suyas
        if getattr(u, 'profile', None) and u.profile.role in ('ADMIN','STAFF'):
            return Reservation.objects.select_related('tour','user').all().order_by('-created_at')
        return Reservation.objects.select_related('tour','user').filter(user=u).order_by('-created_at')

    def perform_create(self, serializer):
        u = self.request.user
        tour = serializer.validated_data['tour']

        # --- Validaciones: blacklist ---
        full_name = f"{u.first_name} {u.last_name}".strip() or u.username
        blocked = BlackList.objects.filter(
            Q(full_name__iexact=full_name) | Q(rut=getattr(u.profile, 'rut', ''))
        ).exists()
        if blocked:
            raise ValueError("Esta persona no puede inscribirse a un tour por mal comportamiento.")

        # cupos suficientes SOLO al confirmar, pero bloquea crear > capacidad teórica
        reserved_now = sum(r.headcount for r in tour.reservations.filter(status='CONFIRMED'))
        requested = 1 + serializer.validated_data.get('guests', 0)
        if reserved_now + requested > tour.capacity:
            raise ValueError("No hay cupos suficientes.")

        # crea en estado PENDING y envía mail a admin
        token = secrets.token_hex(20)
        instance = serializer.save(user=u, status='PENDING', confirm_token=token)

        # notifica admin (en consola si EMAIL_BACKEND=console)
        send_mail(
            subject='Nueva reserva en RutaViva',
            message=f'Usuario {u.username} solicitó reserva en {tour.name}.\nRevisar en el panel /admin.',
            from_email=None, recipient_list=['noreply@rutaviva.cl'], fail_silently=True
        )
        return instance

    @action(detail=True, methods=['POST'], permission_classes=[IsStaff])
    def approve(self, request, pk=None):
        r = self.get_object()
        if r.status not in ('PENDING', 'REJECTED'):
            return Response({'detail':'La reserva ya fue gestionada.'}, status=400)
        r.status = 'WAIT_CLIENT'
        r.save(update_fields=['status'])

        # enviar link de confirmación
        confirm_url = f"{request.build_absolute_uri('/').rstrip('/')}/api/reservations/confirm/{r.confirm_token}/"
        send_mail(
            subject='Confirma tu reserva',
            message=f'Hola {r.user.username}, confirma tu reserva en: {confirm_url}',
            from_email=None, recipient_list=[r.user.email], fail_silently=True
        )
        return Response(ReservationSerializer(r).data)

    @action(detail=True, methods=['POST'], permission_classes=[IsStaff])
    def reject(self, request, pk=None):
        r = self.get_object()
        r.status = 'REJECTED'
        r.save(update_fields=['status'])
        return Response(ReservationSerializer(r).data)


@api_view(['GET'])
@permission_classes([AllowAny])
def confirm_reservation(request, token: str):
    try:
        r = Reservation.objects.select_related('tour').get(confirm_token=token, status='WAIT_CLIENT')
    except Reservation.DoesNotExist:
        return Response({'detail':'Token inválido o reserva ya confirmada.'}, status=400)

    # validar capacidad al confirmar
    reserved_now = sum(x.headcount for x in r.tour.reservations.filter(status='CONFIRMED'))
    if reserved_now + r.headcount > r.tour.capacity:
        r.status = 'REJECTED'
        r.save(update_fields=['status'])
        return Response({'detail':'Sin cupos al momento de confirmar.'}, status=409)

    r.status = 'CONFIRMED'
    r.save(update_fields=['status'])
    return Response({'detail':'Reserva confirmada.'})
