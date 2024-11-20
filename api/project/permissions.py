from rest_framework.permissions import BasePermission
from api.permissions.models import Permissions  # Import Permissions model
from .models import Project  # Import Project model

class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user

class IsManager(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user in obj.managers.all()

class IsNotPersonalProject(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.type != 'personal'

class IsOwnerOrIsManager(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user or request.user in obj.managers.all()

class IsNotTypePersonal(BasePermission):
    def has_permission(self, request, view):
        return request.data.get('type') != 'personal'

class HasProjectPermission(BasePermission):
    """
    Kiểm tra quyền truy cập dự án.
    
    Các quyền được kiểm tra:
    - canEdit: Sửa thông tin
    - canDelete: Xóa dự án  
    - canAdd: Thêm dự án con
    - canFinish: Đánh dấu hoàn thành
    - canAddMember: Thêm thành viên
    - canRemoveMember: Xóa thành viên
    """
    def has_permission(self, request, view):
        if view.action == 'create':
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
            return True

        if obj.owner == request.user:
            return True

        permission_map = {
            'PUT': 'canEdit',
            'PATCH': 'canFinish',
            'DELETE': 'canDelete'
        }

        permission_type = permission_map.get(request.method)
        if permission_type:
            return self.check_permission_recursive(obj, request.user, permission_type)

        return False

    def check_permission_recursive(self, project, user, permission_type):
        """
        Kiểm tra quyền theo cách đệ quy lên cây dự án.
        
        Args:
            project: Dự án cần kiểm tra
            user: Người dùng cần kiểm tra quyền
            permission_type: Loại quyền cần kiểm tra
            
        Returns:
            bool: True nếu người dùng có quyền, False nếu không
        """
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
