from rest_framework.permissions import BasePermission
from .models import Permissions

class IsOwnerOrAdmin(BasePermission):
    """
    Kiểm tra quyền truy cập.
    
    Cho phép truy cập nếu người dùng là chủ sở hữu dự án hoặc là quản trị viên.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj.project.owner == request.user or request.user.is_staff
