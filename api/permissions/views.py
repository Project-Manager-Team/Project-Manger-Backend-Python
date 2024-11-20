from rest_framework import viewsets
from .models import Permissions
from .serializers import PermissionsSerializer
from rest_framework.permissions import IsAuthenticated
from .permissions import IsOwnerOrAdmin
from rest_framework.exceptions import PermissionDenied
from api.project.models import Project
from rest_framework.decorators import action
from rest_framework.response import Response

class PermissionsViewSet(viewsets.ModelViewSet):
    """
    ViewSet để quản lý quyền hạn trong dự án.
    
    Cung cấp các chức năng CRUD cho quyền hạn và các phương thức tùy chỉnh
    để truy vấn quyền hạn theo dự án và người dùng.
    """
    queryset = Permissions.objects.all()
    serializer_class = PermissionsSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def perform_create(self, serializer):
        """
        Tạo mới quyền hạn.
        Chỉ chủ sở hữu dự án mới có thể tạo quyền hạn.
        """
        project = serializer.validated_data['project']
        if project.owner != self.request.user:
            raise PermissionDenied("Only the project owner can modify permissions.")
        serializer.save()

    def perform_update(self, serializer):
        project = serializer.instance.project
        if project.owner != self.request.user:
            raise PermissionDenied("Only the project owner can modify permissions.")
        serializer.save()

    def get_queryset(self):
        project_id = self.request.query_params.get('project_id')
        user_id = self.request.query_params.get('user_id')
        if project_id and user_id:
            return self.queryset.filter(project_id=project_id, user_id=user_id)

        return self.queryset

    @action(detail=False, methods=['GET'])
    def get_by_project_user(self, request):
        """
        Lấy thông tin quyền hạn theo dự án và người dùng.
        
        Tham số query:
            - project_id: ID của dự án
            - user_id: ID của người dùng
        """
        project_id = request.query_params.get('project_id')
        user_id = request.query_params.get('user_id')
        if not project_id or not user_id:
            return Response({"error": "Missing project_id or user_id"}, status=400)
            
        permission = self.queryset.filter(
            project_id=project_id,
            user_id=user_id
        ).first()
        
        if permission:
            serializer = self.get_serializer(permission)
            return Response(serializer.data)
        return Response({"error": "Permission not found"}, status=404)
