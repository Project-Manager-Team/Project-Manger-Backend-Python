from rest_framework.permissions import BasePermission
from api.permissions.models import Permissions  # Import Permissions model
from .models import Project  # Import Project model

class IsOwner(BasePermission):
    # Kiểm tra user là owner của project
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user

class IsManager(BasePermission):
    # Kiểm tra user là manager của project
    def has_object_permission(self, request, view, obj):
        return request.user in obj.managers.all()

class IsNotPersonalProject(BasePermission):
    # Ngăn chặn thao tác trên project loại 'personal'
    def has_object_permission(self, request, view, obj):
        return obj.type != 'personal'

class IsOwnerOrIsManager(BasePermission):
    # Kiểm tra user là owner hoặc manager
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user or request.user in obj.managers.all()

class IsNotTypePersonal(BasePermission):
    # Ngăn chặn tạo project loại 'personal'
    def has_permission(self, request, view):
        return request.data.get('type') != 'personal'

class HasProjectPermission(BasePermission):
    def has_permission(self, request, view):
        if view.action == 'create':
            # Kiểm tra quyền tạo project con
            parent_id = request.data.get('parentId')
            if not parent_id:
                return True
            try:
                parent_project = Project.objects.get(id=parent_id)
                return self.check_permission_recursive(parent_project, request.user, 'canAdd')
            except Project.DoesNotExist:
                return False
        return True

    def has_object_permission(self, request, view, obj):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            # Cho phép các phương thức đọc
            return True

        if obj.owner == request.user:
            # Owner có toàn quyền
            return True

        # Map phương thức HTTP tới loại quyền
        permission_map = {
            'PUT': 'canEdit',
            'PATCH': 'canFinish',
            'DELETE': 'canDelete'
        }

        permission_type = permission_map.get(request.method)
        if permission_type:
            # Kiểm tra quyền bằng cách duyệt ngược lên project cha
            return self.check_permission_recursive(obj, request.user, permission_type)

        return False

    def check_permission_recursive(self, project, user, permission_type):
        current_project = project
        while current_project is not None:
            if current_project.owner == user:
                return True
            try:
                permission = Permissions.objects.get(project=current_project, user=user)
                if getattr(permission, permission_type, False):
                    return True
            except Permissions.DoesNotExist:
                pass
            current_project = current_project.parent
        return False
