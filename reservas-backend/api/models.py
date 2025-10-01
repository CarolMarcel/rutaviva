from django.db import models
from django.contrib.auth.models import User
from django.db import models, transaction
from django.utils import timezone


# -----------------------------
# Perfil y BlackList
# -----------------------------
class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="perfil")
    rol = models.CharField(
        max_length=20,
        choices=[("admin", "admin"), ("colaborador", "colaborador"), ("cliente", "cliente")],
        default="cliente",
    )
    telefono = models.CharField(max_length=20, blank=True, null=True)
    rut = models.CharField(max_length=12, unique=True, null=True, blank=True)  # normalizado
    fecha_nac = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} ({self.rol})"


class BlackList(models.Model):
    cliente = models.ForeignKey(User, on_delete=models.CASCADE, related_name="registros_blacklist")
    motivo = models.CharField(max_length=255)
    vigente = models.BooleanField(default=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["cliente", "vigente"])]

    def __str__(self):
        estado = "vigente" if self.vigente else "inactiva"
        return f"BlackList({self.cliente.username}) - {estado}"


# -----------------------------
# Recursos y Asignaciones
# -----------------------------
class Vehiculo(models.Model):
    patente = models.CharField(max_length=12, unique=True)
    marca = models.CharField(max_length=50, blank=True, null=True)
    modelo = models.CharField(max_length=50, blank=True, null=True)
    anio = models.PositiveSmallIntegerField(blank=True, null=True)
    tipo = models.CharField(max_length=10, choices=[("bus", "bus"), ("van", "van")], default="van")
    capacidad = models.PositiveSmallIntegerField()
    disponible = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.patente} ({self.tipo})"


# -----------------------------
# Evento (la entidad “Tour” del negocio)
# -----------------------------
class Evento(models.Model):
    nombre = models.CharField(max_length=120)
    ubicacion = models.CharField(max_length=120)
    fecha = models.DateField()
    hora = models.TimeField()
    duracion_min = models.PositiveSmallIntegerField(default=60)
    capacidad = models.PositiveIntegerField(default=30)  # por defecto 30 cupos
    descripcion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)
    # Si luego quieres imagen:
    # imagen = models.URLField(blank=True, null=True)

    @property
    def reserved_count(self):
        """Cantidad de cupos confirmados (suma de 'cantidad' en reservas confirmadas)."""
        return self.reservas.filter(estado="confirmed").aggregate(
            total=models.Sum("cantidad")
        ).get("total") or 0

    @property
    def cupos_disponibles(self):
        """Capacidad restante no comprometida por reservas confirmadas."""
        return max(self.capacidad - self.reserved_count, 0)

    def __str__(self):
        return f"{self.nombre} ({self.fecha} {self.hora})"

    class Meta:
        indexes = [
            models.Index(fields=["fecha"]),
            models.Index(fields=["activo"]),
        ]


class Colaborador(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    rol_colab = models.CharField(max_length=10, choices=[("guia", "guia"), ("chofer", "chofer")])
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.usuario.username} ({self.rol_colab})"


class Asignacion(models.Model):
    evento = models.OneToOneField(Evento, on_delete=models.CASCADE, related_name="asignacion")
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.SET_NULL, null=True, blank=True)
    guia = models.ForeignKey(
        Colaborador, on_delete=models.SET_NULL, null=True, blank=True, related_name="asignaciones_guia"
    )
    chofer = models.ForeignKey(
        Colaborador, on_delete=models.SET_NULL, null=True, blank=True, related_name="asignaciones_chofer"
    )

    def __str__(self):
        partes = [f"Evento {self.evento_id}"]
        if self.vehiculo_id:
            partes.append(f"Vehículo {self.vehiculo.patente}")
        if self.guia_id:
            partes.append(f"Guía {self.guia.usuario.username}")
        if self.chofer_id:
            partes.append(f"Chofer {self.chofer.usuario.username}")
        return " | ".join(partes)


# -----------------------------
# Reservas + Invitados
# -----------------------------
class Reserva(models.Model):
    ESTADOS = [
        ("pending_admin", "Pendiente admin"),
        ("admin_rejected", "Rechazada por admin"),
        ("pending_client", "Pendiente confirmación cliente"),
        ("confirmed", "Confirmada"),
        ("cancelled", "Cancelada"),
    ]

    cliente = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reservas")
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name="reservas")
    cantidad = models.PositiveSmallIntegerField()
    estado = models.CharField(max_length=20, choices=ESTADOS, default="pending_admin")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    token_confirmacion = models.CharField(max_length=64, blank=True, null=True, db_index=True)

    # --- Validaciones de dominio ---
    def clean(self):
        # 1) cantidad > 0
        if self.cantidad is None or self.cantidad < 1:
            from django.core.exceptions import ValidationError
            raise ValidationError("La cantidad debe ser al menos 1.")

        # 2) Evento en fecha válida
        if self.evento.fecha < timezone.localdate():
            from django.core.exceptions import ValidationError
            raise ValidationError("El evento ya ocurrió. No se admiten reservas en pasado.")

        # 3) Capacidad (no sobrepasar cupos). Si es update y estaba confirmada, devolver cupos previos.
        if self.estado != "cancelled":
            disponibles = self.evento.cupos_disponibles
            if self.pk:
                original = Reserva.objects.get(pk=self.pk)
                if original.estado == "confirmed":
                    disponibles += original.cantidad
            if self.cantidad > disponibles:
                from django.core.exceptions import ValidationError
                raise ValidationError(f"No hay suficientes cupos disponibles. Cupos libres: {disponibles}.")

    def save(self, *args, **kwargs):
        # Ejecutar validaciones antes de guardar
        self.full_clean()
        return super().save(*args, **kwargs)

    # --- Helpers ---
    def puede_confirmarse(self) -> bool:
        return self.estado in ("pending_client", "pending_admin")

    def confirmar_por_token(self, token: str) -> bool:
        """Confirma la reserva si el token coincide y el estado permite confirmación."""
        if not token or token != self.token_confirmacion:
            return False
        if not self.puede_confirmarse():
            return False
        self.estado = "confirmed"
        self.token_confirmacion = None
        self.save(update_fields=["estado", "token_confirmacion"])
        return True

    def cancelar(self, motivo: str = ""):
        if self.estado != "cancelled":
            self.estado = "cancelled"
            self.save(update_fields=["estado"])

    def __str__(self):
        return f"Reserva #{self.pk} - {self.evento.nombre} x{self.cantidad} ({self.estado})"

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(cantidad__gt=0), name="reserva_cantidad_gt_0"),
        ]
        indexes = [
            models.Index(fields=["cliente", "estado"]),
            models.Index(fields=["evento", "estado"]),
            models.Index(fields=["-fecha_creacion"]),
        ]


class InvitadoReserva(models.Model):
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE, related_name="invitados")
    rut_invitado = models.CharField(max_length=12, null=True, blank=True)
    nombre_invitado = models.CharField(max_length=100)
    edad_invitado = models.PositiveSmallIntegerField(null=True, blank=True)

    def __str__(self):
        return f"Invitado({self.nombre_invitado}) de Reserva #{self.reserva_id}"