from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.db import transaction
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Perfil, Evento, Reserva, BlackList, Asignacion, Colaborador, Vehiculo
from .serializers import UserSerializer, EventoSerializer, ReservaSerializer, TourPublicSerializer
from .permissions import IsAdmin
from .email_adapter import enviar_correo
from .tokens import generar_token
from rest_framework import generics, permissions



@api_view(["GET"])
def health(request):
    return Response({"status":"ok"})

# --------- AUTH ---------
@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    data = request.data
    if not all(k in data for k in ["username","email","password","rol"]):
        return Response({"detail":"Datos incompletos"}, status=400)
    if User.objects.filter(username=data["username"]).exists():
        return Response({"detail":"Usuario ya existe"}, status=400)
    user = User.objects.create_user(username=data["username"], email=data["email"], password=data["password"])
    Perfil.objects.create(user=user, rol=data.get("rol","cliente"))
    return Response(UserSerializer(user).data, status=201)

@api_view(["POST"])
@permission_classes([AllowAny])
def login_jwt(request):
    username = request.data.get("username")
    password = request.data.get("password")
    user = authenticate(username=username, password=password)
    if not user:
        return Response({"detail":"Credenciales inválidas"}, status=401)
    refresh = RefreshToken.for_user(user)
    return Response({"access": str(refresh.access_token), "refresh": str(refresh)})

@api_view(["GET"])
def me(request):
    return Response({"user": UserSerializer(request.user).data, "rol": getattr(request.user.perfil,"rol",None)})

# --------- EVENTOS ---------
@api_view(["GET","POST"])
def eventos_list(request):
    if request.method == "GET":
        qs = Evento.objects.filter(activo=True).order_by("fecha","hora")
        return Response(EventoSerializer(qs, many=True).data)
    # POST solo admin (crear)
    if not IsAdmin().has_permission(request, None):
        return Response({"detail":"Solo admin"}, status=403)
    ser = EventoSerializer(data=request.data)
    if ser.is_valid():
        ser.save()
        return Response(ser.data, status=201)
    return Response(ser.errors, status=400)

@api_view(["GET","PUT","DELETE"])
def evento_crud_admin(request, evento_id:int):
    try:
        ev = Evento.objects.get(id=evento_id)
    except Evento.DoesNotExist:
        return Response({"detail":"No encontrado"}, status=404)
    if request.method == "GET":
        return Response(EventoSerializer(ev).data)
    if not IsAdmin().has_permission(request, None):
        return Response({"detail":"Solo admin"}, status=403)
    if request.method == "PUT":
        ser = EventoSerializer(ev, data=request.data, partial=True)
        if ser.is_valid():
            ser.save()
            return Response(ser.data)
        return Response(ser.errors, status=400)
    if request.method == "DELETE":
        ev.delete()
        return Response(status=204)

# --------- RESERVAS ---------
def _esta_en_blacklist(user:User)->bool:
    return BlackList.objects.filter(cliente=user, vigente=True).exists()

@api_view(["POST"])
def crear_reserva(request):
    user = request.user
    data = request.data.copy()
    data["cliente"] = user.id
    # Validación rápida
    try:
        ev = Evento.objects.get(id=data.get("evento"))
    except Evento.DoesNotExist:
        return Response({"detail":"Evento inválido"}, status=400)

    # BlackList cliente (e invitados en frontend)
    if _esta_en_blacklist(user):
        return Response({"detail":"Esta persona no puede inscribirse por mal comportamiento"}, status=403)

    ser = ReservaSerializer(data=data)
    if not ser.is_valid():
        return Response(ser.errors, status=400)
    reserva = ser.save()  # queda pending_admin

    # Notifica admin
    enviar_correo(
        destinatario="admin@rutaviva.cl",
        asunto="Nueva reserva pendiente de revisión",
        cuerpo=f"Reserva #{reserva.id} de {user.username} para evento {ev.nombre}"
    )
    return Response(ReservaSerializer(reserva).data, status=201)

@api_view(["GET"])
def reservas_admin(request):
    if not IsAdmin().has_permission(request, None):
        return Response({"detail":"Solo admin"}, status=403)
    qs = Reserva.objects.select_related("evento","cliente").order_by("-fecha_creacion")
    return Response(ReservaSerializer(qs, many=True).data)

@api_view(["POST"])
def aprobar_rechazar_reserva(request, reserva_id:int):
    if not IsAdmin().has_permission(request, None):
        return Response({"detail":"Solo admin"}, status=403)
    accion = request.data.get("accion")  # "aprobar" | "rechazar"
    try:
        rs = Reserva.objects.select_related("evento","cliente").get(id=reserva_id)
    except Reserva.DoesNotExist:
        return Response({"detail":"No encontrada"}, status=404)

    if accion == "rechazar":
        rs.estado = "admin_rejected"
        rs.save()
        enviar_correo(rs.cliente.email, "Reserva rechazada", f"Tu reserva #{rs.id} fue rechazada.")
        return Response({"ok":True})

    if accion == "aprobar":
        # genera token y pasa a pending_client
        token = generar_token()
        rs.token_confirmacion = token
        rs.estado = "pending_client"
        rs.save()
        link = f'{settings.FRONTEND_URL}/confirmar/{token}'
        enviar_correo(rs.cliente.email, "Confirma tu reserva", f"Para confirmar tu reserva #{rs.id}, haz clic: {link}")
        return Response({"ok":True})

    return Response({"detail":"Acción inválida"}, status=400)

@api_view(["GET"])
@permission_classes([AllowAny])  # lo usa el link por correo
@transaction.atomic
def confirmar_reserva(request, token:str):
    try:
        rs = Reserva.objects.select_related("evento").get(token_confirmacion=token, estado="pending_client")
    except Reserva.DoesNotExist:
        return Response({"detail":"Token inválido o expirado"}, status=400)

    ev = rs.evento
    if ev.capacidad - ev.reserved_count < rs.cantidad:
        rs.estado = "cancelled"
        rs.save()
        return Response({"detail":"Sin cupos disponibles"}, status=409)

    rs.estado = "confirmed"
    rs.save()
    # actualiza contador
    ev.reserved_count = ev.reserved_count + rs.cantidad
    ev.save()

    enviar_correo(rs.cliente.email, "Reserva confirmada", f"Tu reserva #{rs.id} fue confirmada.")
    return Response({"ok":True})
    
# --------- BLACKLIST / ASIGNACIÓN ---------
@api_view(["POST"])
def blacklist_toggle(request, user_id:int):
    if not IsAdmin().has_permission(request, None):
        return Response({"detail":"Solo admin"}, status=403)
    try:
        u = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"detail":"Usuario no existe"}, status=404)
    vigente = request.data.get("vigente", True)
    motivo = request.data.get("motivo", "Comportamiento indebido")
    if vigente:
        BlackList.objects.create(cliente=u, motivo=motivo, vigente=True)
    else:
        BlackList.objects.filter(cliente=u, vigente=True).update(vigente=False)
    return Response({"ok":True})

@api_view(["POST"])
def asignacion_upsert(request, evento_id:int):
    if not IsAdmin().has_permission(request, None):
        return Response({"detail":"Solo admin"}, status=403)
    try:
        ev = Evento.objects.get(id=evento_id)
    except Evento.DoesNotExist:
        return Response({"detail":"Evento no encontrado"}, status=404)

    vehiculo_id = request.data.get("vehiculo_id")
    guia_id = request.data.get("guia_id")
    chofer_id = request.data.get("chofer_id")

    asg, _ = Asignacion.objects.get_or_create(evento=ev)
    if vehiculo_id: asg.vehiculo_id = vehiculo_id
    if guia_id: asg.guia_id = guia_id
    if chofer_id: asg.chofer_id = chofer_id
    asg.save()
    return Response({"ok":True})

class TourListView(generics.ListAPIView):
    queryset = Evento.objects.filter(activo=True).order_by("fecha", "hora")
    serializer_class = TourPublicSerializer
    permission_classes = [permissions.AllowAny]

class TourDetailView(generics.RetrieveAPIView):
    queryset = Evento.objects.all()
    serializer_class = TourPublicSerializer
    permission_classes = [permissions.AllowAny]

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def mis_reservas(request):
    qs = Reserva.objects.filter(cliente=request.user).select_related("evento").order_by("-fecha_creacion")
    return Response(ReservaSerializer(qs, many=True).data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def cancelar_reserva(request, reserva_id:int):
    try:
        rs = Reserva.objects.get(id=reserva_id, cliente=request.user)
    except Reserva.DoesNotExist:
        return Response({"detail": "No encontrada"}, status=404)

    if rs.estado == "cancelled":
        return Response({"detail": "La reserva ya estaba cancelada."}, status=200)

    rs.estado = "cancelled"
    rs.save(update_fields=["estado"])
    return Response({"detail": "Reserva cancelada."}, status=200)