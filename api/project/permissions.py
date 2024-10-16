from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class IsManager(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.mananger == request.user


class IsNotPersonalProject(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.type != 'personal'


class IsOwnerOrIsManger(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user or obj.mananger == request.user


class IsNotTypePersonal(BasePermission):
    def has_permission(self, request, view):
        return request.data.get('type') != 'personal'
