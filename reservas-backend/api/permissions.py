from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        u = request.user
        return bool(u and u.is_authenticated and getattr(u, 'profile', None) and u.profile.role == 'ADMIN')

class IsStaff(BasePermission):
    def has_permission(self, request, view):
        u = request.user
        return bool(u and u.is_authenticated and getattr(u, 'profile', None) and u.profile.role in ('ADMIN','STAFF'))

