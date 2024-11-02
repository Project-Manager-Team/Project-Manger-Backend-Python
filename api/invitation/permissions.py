from rest_framework.permissions import BasePermission

class IsReceiver(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.receiver == request.user
