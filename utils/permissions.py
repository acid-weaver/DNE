from rest_framework.permissions import BasePermission

from user.models import User


class AdminPermission(BasePermission):
    """Full access for admin."""

    def has_permission(self, request, view):
        user = request.user
        if user.is_superuser:
            return True
        return False
    

class SelfPermission(BasePermission):
    """Access to self owned resources + create."""

    def has_permission(self, request, view):
        if request.method == 'POST':
            return True
        return False
    
    def has_object_permission(self, request, view, obj):
        return obj.id == request.user.id
