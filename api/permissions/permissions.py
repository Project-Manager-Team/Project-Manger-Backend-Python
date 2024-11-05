from rest_framework.permissions import BasePermission
from .models import Permissions

class IsOwnerOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj.project.owner == request.user or request.user.is_staff
