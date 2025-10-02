# api/models.py
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

class Profile(models.Model):
    ROLE_CHOICES = (
        ('CLIENT', 'Cliente'),
        ('ADMIN', 'Administrador'),
        ('STAFF', 'Colaborador'),
    )
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='CLIENT')
    rut = models.CharField(max_length=12, blank=True)  # opcional
    birthdate = models.DateField(null=True, blank=True)

    def __str__(self):
        return f'{self.user.username} ({self.role})'


class BlackList(models.Model):
    full_name = models.CharField(max_length=150)
    rut = models.CharField(max_length=12, blank=True)
    birthdate = models.DateField(null=True, blank=True)
    reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Persona bloqueada"
        verbose_name_plural = "Personas bloqueadas"

    def __str__(self):
        return self.full_name


class Tour(models.Model):
    name = models.CharField(max_length=120)
    location = models.CharField(max_length=120)
    date = models.DateField()
    time = models.TimeField()
    capacity = models.PositiveIntegerField(default=20)
    description = models.TextField()
    price_clp = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.location} {self.date}"


class Reservation(models.Model):
    STATUS = (
        ('PENDING', 'Reserva por confirmar'),
        ('WAIT_CLIENT', 'Pendiente confirmación del cliente'),
        ('CONFIRMED', 'Confirmada'),
        ('REJECTED', 'Rechazada'),
    )
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='reservations')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reservations')
    status = models.CharField(max_length=15, choices=STATUS, default='PENDING')
    guests = models.PositiveIntegerField(default=0)  # invitados adicionales
    created_at = models.DateTimeField(auto_now_add=True)
    confirm_token = models.CharField(max_length=64, blank=True)

    class Meta:
        unique_together = ('tour', 'user')  # 1 reserva por tour-usuario

    def __str__(self):
        return f"{self.user.username} -> {self.tour} [{self.status}]"

    @property
    def headcount(self):
        return 1 + self.guests


class CulturalEvent(models.Model):
    title = models.CharField(max_length=150)
    date = models.DateField()
    city = models.CharField(max_length=100)
    summary = models.TextField(blank=True)

    def __str__(self):
        return f"{self.title} - {self.city} ({self.date})"
