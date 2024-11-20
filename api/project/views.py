from rest_framework import viewsets
from ..models import Project
from .serializers import ProjectSerializer, RecursiveProjectSerializer, RecursiveProjectReportSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .permissions import *
from .permissions import HasProjectPermission
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from .tasks import update_parent_progress
from rest_framework.exceptions import ValidationError 
from django.db.models import Prefetch
from django.contrib.auth.models import User
from api.permissions.models import Permissions
from mptt.utils import get_cached_trees
from django.utils import timezone
from typing import Union, List, Dict, Any
from django.http import HttpRequest

# Hàm để xây dựng cây project dưới dạng dictionary
def get_project_tree(root: Project) -> Dict[str, Any]:
    serializer = RecursiveProjectSerializer(root)
    return serializer.data

def get_project_report_tree(root: Project, context: Dict[str, Any]) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
    serializer = RecursiveProjectReportSerializer(root, context=context)
    return serializer.data

class PersonalProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    authentication_classes = [JWTAuthentication]

    def get_permissions(self) -> List[Any]:
        # Xác định permissions dựa trên action
        if self.action == 'destroy':
            return [IsAuthenticated(), HasProjectPermission(), IsNotPersonalProject()]
        if self.action == 'create':
            return [IsAuthenticated(), HasProjectPermission(), IsNotTypePersonal()]
        if self.action == 'update':
            return [IsAuthenticated(), HasProjectPermission(), IsNotPersonalProject()]
        return [IsAuthenticated(), HasProjectPermission()]

    def get_queryset(self) -> Any:
        # Lấy danh sách projects mà user có quyền truy cập
        user = self.request.user
        # Lấy personal project của user
        root = get_object_or_404(
            self.queryset.select_related('owner').prefetch_related('managers'),
            owner=user, type="personal"
        )
        # Lấy tất cả descendants của personal project
        all_descendants = root.get_descendants(include_self=True).distinct().prefetch_related('managers')
        # Thêm projects mà user là manager
        for project in self.queryset.filter(managers=user).prefetch_related('managers'):
            all_descendants |= project.get_descendants(include_self=True).prefetch_related('managers').distinct()
        return all_descendants.order_by('id').distinct()

    def perform_create(self, serializer: ProjectSerializer) -> None:
        try:
            # Lưu project mới với owner là user hiện tại và progress = 0
            response = serializer.save(owner=self.request.user, progress=0)
            # Cập nhật progress cho project cha (nếu có)
            update_parent_progress.delay(serializer.validated_data.get('parentId'))
            return response
        except ValidationError as e:
            raise ValidationError({"detail": e.detail})
    
    def perform_update(self, serializer: ProjectSerializer) -> None:
        obj = serializer.instance
        self.check_object_permissions(self.request, obj)
        try:
            progress = serializer.validated_data.get('progress')
            if progress is not None:
                # Set completeTime when progress reaches 100%
                if progress >= 100 and not obj.completeTime:
                    serializer.validated_data['completeTime'] = timezone.now()
                # Reset completeTime if progress is less than 100%
                elif progress < 100 and obj.completeTime:
                    serializer.validated_data['completeTime'] = None
                update_parent_progress.delay(obj.parent.id)
            super().perform_update(serializer)
        except ValidationError as e:
            raise ValidationError({"detail": e.detail})
    
    def perform_destroy(self, instance: Project) -> None:
        # Kiểm tra permissions trước khi xóa
        self.check_object_permissions(self.request, instance)
        parent_id = instance.parent.id
        if instance.owner == self.request.user:            
            # Nếu là owner, xóa project
            super().perform_destroy(instance)
            update_parent_progress.delay(parent_id)
        else:
            # Nếu không phải owner, chỉ xóa user khỏi managers
            instance.managers.remove(self.request.user)
            instance.save()
        return None

    @action(detail=False, methods=['GET'])
    def personal(self, request: HttpRequest) -> Response:
        # Return personal projects owned by the user
        queryset = get_object_or_404(self.get_queryset(),owner=request.user, type="personal").get_children()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'])
    def managed(self, request: HttpRequest) -> Response:
        # Return projects managed by the user
        queryset = self.get_queryset().filter(managers=request.user).distinct()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['GET'])
    def child(self, request: HttpRequest, pk: Union[str, None] = None) -> Response:
        # Lấy các project con trực tiếp của project hiện tại
        queryset = get_object_or_404(self.get_queryset(), id=pk).get_children()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['GET'])
    def tree_personal(self, request: HttpRequest) -> Response:
        # Get the root project and all its descendants
        root = get_object_or_404(self.get_queryset(), type="personal", parent=None, owner=request.user)
        tree = get_project_tree(root)
        return Response(tree, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['GET'])
    def managed_tree(self, request: HttpRequest) -> Response:
        # Get all projects managed by the user
        managed_projects = self.get_queryset().filter(managers=request.user)
        
        # Get the root nodes (projects that are directly managed)
        root_nodes = [project for project in managed_projects 
                     if not any(p in managed_projects for p in project.get_ancestors())]
        
        # Build tree structure for each root node
        trees = []
        for root in root_nodes:
            trees.append(get_project_tree(root))
            
        return Response(trees, status=status.HTTP_200_OK)

    
    @action(detail=True, methods=['GET'])
    def managers_permissions(self, request: HttpRequest, pk: Union[str, None] = None) -> Response:
        project = get_object_or_404(
            self.get_queryset().prefetch_related(
                'managers__userprofile',
                Prefetch('permissions', queryset=Permissions.objects.filter(project_id=pk))
            ),
            id=pk
        )
        permissions_dict = {permission.user_id: permission for permission in project.permissions.all()}

        data = []
        for manager in project.managers.all():
            perm = permissions_dict.get(manager.id)
            if perm:
                data.append({
                    "user": {
                        "id": manager.id,
                        "username": manager.username,
                        "avatar": manager.userprofile.avatar.url if hasattr(manager, 'userprofile') and manager.userprofile.avatar else None
                    },
                    "permission_id": perm.id,
                    "permissions": {
                        'canEdit': perm.canEdit,
                        'canDelete': perm.canDelete,
                        'canAdd': perm.canAdd,
                        'canFinish': perm.canFinish,
                        'canAddMember': perm.canAddMember,     
                        'canRemoveMember': perm.canRemoveMember 
                    }
                })
            else:
                data.append({
                    "user": {
                        "id": manager.id,
                        "username": manager.username,
                        "avatar": manager.userprofile.avatar.url if hasattr(manager, 'userprofile') and manager.userprofile.avatar else None
                    },
                    "permission_id": None,
                    "permissions": None
                })
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['POST'], permission_classes=[IsAuthenticated, HasProjectPermission])
    def remove_manager(self, request: HttpRequest, pk: Union[str, None] = None) -> Response:
        project = self.get_object()
        self.check_object_permissions(request, project)
        
        if not (project.owner == request.user or 
                Permissions.objects.filter(project=project, 
                                        user=request.user, 
                                        canRemoveMember=True).exists()):
            return Response(
                {'detail': 'Bạn không có quyền xóa thành viên khỏi dự án này.'}, 
                status=status.HTTP_403_FORBIDDEN
            )
                          
        manager_id = request.data.get('managerId')
        if not manager_id:
            return Response({'detail': 'Manager ID is required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            manager = User.objects.get(id=manager_id)
            if manager in project.managers.all():
                project.managers.remove(manager)
                Permissions.objects.filter(project=project, user=manager).delete()
                return Response({'detail': 'Manager removed successfully.'}, status=status.HTTP_200_OK)
            else:
                return Response({'detail': 'User is not a manager of this project.'}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({'detail': 'Manager not found.'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['GET'])
    def report(self, request: HttpRequest, pk: Union[str, None] = None) -> Response:
        project = self.get_object()
        tree = get_project_report_tree(project, {'request': request})
        return Response(tree, status=status.HTTP_200_OK)



