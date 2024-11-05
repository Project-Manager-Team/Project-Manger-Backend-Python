from rest_framework import viewsets
from ..models import Project
from .serializers import ProjectSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .permissions import *
from .permissions import HasProjectPermission
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from rest_framework import status
from .tasks import update_parent_progress
from django.forms.models import model_to_dict
from rest_framework.exceptions import ValidationError 
from api.permissions.serializers import PermissionsSerializer
from django.db.models import Prefetch

# Hàm để xây dựng cây project dưới dạng dictionary
def build_tree(root):
    # Chuyển project thành dictionary
    tree_dict = model_to_dict(root)
    # Đệ quy cho các project con
    tree_dict['children'] = [build_tree(child) for child in  root.get_children().order_by('id')] 
    return tree_dict

class PersonalProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        # Xác định permissions dựa trên action
        if self.action == 'destroy':
            return [IsAuthenticated(), HasProjectPermission(), IsNotPersonalProject()]
        if self.action == 'create':
            return [IsAuthenticated(), HasProjectPermission(), IsNotTypePersonal()]
        if self.action == 'update':
            return [IsAuthenticated(), HasProjectPermission(), IsNotPersonalProject()]
        return [IsAuthenticated(), HasProjectPermission()]

    def get_queryset(self):
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

    def perform_create(self, serializer):
        try:
            # Lưu project mới với owner là user hiện tại và progress = 0
            response = serializer.save(owner=self.request.user, progress=0)
            # Cập nhật progress cho project cha (nếu có)
            update_parent_progress.delay(serializer.validated_data.get('parentId'))
            return response
        except ValidationError as e:
            raise ValidationError({"detail": e.detail})
    
    def perform_update(self, serializer):
        obj = serializer.instance
        # Kiểm tra permissions trước khi cập nhật
        self.check_object_permissions(self.request, obj)
        try:
            # Nếu có progress mới, cập nhật progress cho project cha
            progress = serializer.validated_data.get('progress')
            if progress is not None:
                update_parent_progress.delay(obj.parent.id)
            super().perform_update(serializer)
        except ValidationError as e:
            raise ValidationError({"detail": e.detail})
    
    def perform_destroy(self, instance):
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
    def personal(self, request):
        # Lấy danh sách personal projects của user
        query_set = self.get_queryset()
        root = get_object_or_404(query_set.select_related('owner'), owner=request.user, type="personal")
        # Lấy các project con trực tiếp và các project mà user là manager
        children_and_managed = query_set.filter(
            Q(parent=root) | Q(managers=request.user) | Q(type="personal")
        ).distinct().prefetch_related('managers')
        serializer = self.get_serializer(children_and_managed, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['GET'])
    def child(self, request, pk=None):
        # Lấy các project con trực tiếp của project hiện tại
        queryset = get_object_or_404(self.get_queryset(), id=pk).get_children()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['GET'])
    def descendants(self, request, pk=None):
        # Lấy toàn bộ cây project con
        root = get_object_or_404(self.get_queryset(), id=pk)
        tree = build_tree(root)
        return Response(tree, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['GET'])
    def managers_permissions(self, request, pk=None):
        # Lấy project và prefetch managers cùng với permissions
        project = get_object_or_404(
            self.get_queryset().prefetch_related(
                'managers__userprofile',
                Prefetch('permissions', queryset=Permissions.objects.filter(project_id=pk))
            ),
            id=pk
        )
        # Tạo mapping từ user_id đến Permission
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
                        'canFinish': perm.canFinish
                    }
                })
            else:
                # Trường hợp không tìm thấy Permission (hiếm khi xảy ra)
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



