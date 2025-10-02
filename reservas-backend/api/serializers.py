from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile, Tour, Reservation, CulturalEvent

class UserSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source='profile.role', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        # password se guarda encriptada por Django
        user = User.objects.create_user(**validated_data)
        return user


class TourSerializer(serializers.ModelSerializer):
    reserved = serializers.SerializerMethodField()
    available = serializers.SerializerMethodField()

    class Meta:
        model = Tour
        fields = ['id','name','location','date','time','capacity','description','price_clp','is_active','reserved','available']

    def get_reserved(self, obj):
        # solo reservas CONFIRMADAS cuentan
        return sum(r.headcount for r in obj.reservations.filter(status='CONFIRMED'))

    def get_available(self, obj):
        return max(0, obj.capacity - self.get_reserved(obj))


class ReservationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    tour_detail = TourSerializer(source='tour', read_only=True)

    class Meta:
        model = Reservation
        fields = ['id','tour','tour_detail','user','guests','status','created_at']


class CulturalEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = CulturalEvent
        fields = ['id','title','date','city','summary']

