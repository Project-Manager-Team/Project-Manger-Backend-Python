from rest_framework.permissions import BasePermission


class isOwnerOrManager(BasePermission):
    def has_object_permission(self, request, view, obj):
        print(1)
        user = request.user
        current = obj

        while current is not None:
            if current.owner == user or current.manager == user:
                return True
            current = current.parent

        return False
