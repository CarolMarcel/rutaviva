from rest_framework import serializers
from django.contrib.auth.models import User
from django.db.models import Sum
from django.utils import timezone

from .models import (Perfil, Vehiculo, Evento, Reserva,
    InvitadoReserva, Asignacion, Colaborador, BlackList
)

# Usuarios

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]


class UserMeSerializer(serializers.ModelSerializer):
    # expone el rol desde Perfil
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "role"]

    def get_role(self, obj):
        try:
            return obj.perfil.rol  # 'cliente' | 'colaborador' | 'admin'
        except Perfil.DoesNotExist:
            return "cliente"


class PerfilSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Perfil
        fields = ["user", "rol", "telefono", "rut", "fecha_nac"]



# Eventos

class EventoSerializer(serializers.ModelSerializer):
    # Campos calculados de forma segura (aunque no existan como @property)
    reserved_count = serializers.SerializerMethodField()
    cupos_disponibles = serializers.SerializerMethodField()

    class Meta:
        model = Evento
        fields = [
            "id", "nombre", "ubicacion", "fecha", "hora", "duracion_min",
            "capacidad", "reserved_count", "cupos_disponibles",
            "descripcion", "activo"
        ]

    def get_reserved_count(self, obj):
        # Si tu modelo Evento tiene @property reserved_count, úsalo:
        if hasattr(obj, "reserved_count") and not callable(obj.reserved_count):
            # Campo en BD (si lo mantuviste). Si lo quitaste, cae al aggregate.
            return obj.reserved_count or 0
        if hasattr(obj, "reserved_count") and callable(obj.reserved_count):
            return obj.reserved_count()

        # Agregado por reservas confirmadas
        return obj.reservas.filter(estado="confirmed").aggregate(
            total=Sum("cantidad")
        ).get("total") or 0

    def get_cupos_disponibles(self, obj):
        # Si tu modelo Evento tiene @property cupos_disponibles, úsalo:
        if hasattr(obj, "cupos_disponibles") and callable(obj.cupos_disponibles):
            return obj.cupos_disponibles()

        reserved = self.get_reserved_count(obj)
        return max((obj.capacidad or 0) - reserved, 0)



# Reservas + Invitados

class InvitadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvitadoReserva
        fields = ["id", "rut_invitado", "nombre_invitado", "edad_invitado"]


class ReservaSerializer(serializers.ModelSerializer):
    invitados = InvitadoSerializer(many=True, required=False)

    class Meta:
        model = Reserva
        fields = ["id", "cliente", "evento", "cantidad", "estado", "fecha_creacion", "invitados"]
        read_only_fields = ["estado", "fecha_creacion", "cliente"]

    def validate(self, data):
        request = self.context.get("request")
        user = getattr(request, "user", None)

        # 1) Blacklist vigente
        if user and BlackList.objects.filter(cliente=user, vigente=True).exists():
            raise serializers.ValidationError(
                "Tu cuenta se encuentra bloqueada para reservas."
            )

        # 2) Evento válido, activo y en fecha futura
        evento = data.get("evento") or getattr(self.instance, "evento", None)
        if not evento:
            raise serializers.ValidationError("Debe indicar un evento válido.")
        if not evento.activo:
            raise serializers.ValidationError("El evento no está disponible para reservas.")

        hoy = timezone.localdate()
        if evento.fecha < hoy:
            raise serializers.ValidationError("El evento ya ocurrió. No se admiten reservas en pasado.")

        # 3) Capacidad disponible (no exceder cupos)
        cantidad = data.get("cantidad") or getattr(self.instance, "cantidad", 0)
        if cantidad < 1:
            raise serializers.ValidationError("La cantidad debe ser al menos 1.")

        # reserved_count robusto
        reserved_count = evento.reservas.filter(estado="confirmed").aggregate(
            total=Sum("cantidad")
        ).get("total") or 0

        disponibles = max((evento.capacidad or 0) - reserved_count, 0)

        # Si es update y la reserva original estaba confirmada, devolver sus cupos
        if self.instance and self.instance.estado == "confirmed":
            disponibles += self.instance.cantidad

        if cantidad > disponibles:
            raise serializers.ValidationError(
                f"No hay suficientes cupos disponibles. Cupos libres: {disponibles}."
            )

        return data

    def create(self, validated_data):
        # invitados embebidos
        invitados = validated_data.pop("invitados", [])
        # setear cliente desde request.user (read_only en Meta)
        request = self.context.get("request")
        user = getattr(request, "user", None)
        validated_data["cliente"] = user

        # estado por defecto lo pone el modelo ("pending_admin"); si quieres, cámbialo aquí
        # validated_data.setdefault("estado", "pending_admin")

        reserva = Reserva.objects.create(**validated_data)
        for inv in invitados:
            InvitadoReserva.objects.create(reserva=reserva, **inv)
        return reserva

    def update(self, instance, validated_data):
        # permitir actualizar cantidad/invitados si lo necesitas
        invitados = validated_data.pop("invitados", None)
        instance = super().update(instance, validated_data)

        if invitados is not None:
            instance.invitados.all().delete()
            for inv in invitados:
                InvitadoReserva.objects.create(reserva=instance, **inv)
        return instance

class TourPublicSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="nombre")
    date = serializers.DateField(source="fecha")
    time = serializers.TimeField(source="hora")
    capacity = serializers.IntegerField(source="capacidad")
    description = serializers.CharField(source="descripcion", allow_blank=True, allow_null=True)
    active = serializers.BooleanField(source="activo")
    reservedCount = serializers.SerializerMethodField()
    remaining = serializers.SerializerMethodField()
    # si más adelante agregas un campo imagen en Evento:
    # image = serializers.CharField(source="imagen", required=False, allow_null=True, default=None)

    class Meta:
        model = Evento
        fields = ("id","name","date","time","capacity","description","active","reservedCount","remaining")

    def get_reservedCount(self, obj):
        return obj.reservas.filter(estado="confirmed").aggregate(
            total=Sum("cantidad")
        ).get("total") or 0

    def get_remaining(self, obj):
        reserved = self.get_reservedCount(obj)
        return max((obj.capacidad or 0) - reserved, 0)

