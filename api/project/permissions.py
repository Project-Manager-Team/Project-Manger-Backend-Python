from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == self.request.user


class IsManager(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.mananger == self.request.user


class IsNotPersonal(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.type != 'personal'


class IsNotTask(BasePermission):
    def has_object_permission(self, request, view, obj):
        ...


class IsOwnerOrManager(BasePermission):
    def has_object_permission(self, request, viewm, obj):
        return obj.mananger == self.request.user or obj.mananger == self.request.user


