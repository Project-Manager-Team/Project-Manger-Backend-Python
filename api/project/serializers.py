from rest_framework import serializers
from ..models import Project
from django.contrib.auth.models import User
from django.utils import timezone
from api.permissions.serializers import PermissionsSerializer

class ProjectSerializer(serializers.ModelSerializer):
    """
    Serializer cho model Project.
    
    Chức năng:
    - Chuyển đổi dữ liệu JSON/Python 
    - Xử lý tạo/cập nhật dự án
    - Quản lý danh sách managers
    - Kiểm tra ràng buộc dữ liệu
    """
    parentId = serializers.IntegerField(required=False, allow_null=True)
    managersCount = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = ['id', 'title','color', 'description', 'beginTime', 'completeTime',
                  'endTime', 'type', 'managersCount', 'owner', 'parentId', 'progress', 
                  'diffLevel', 'permissions'] 
    
    def get_managersCount(self, obj):
        """
        Đếm số lượng người quản lý của dự án.
        Returns:
            int: Số lượng manager
        """
        return obj.managers.count()
    
    def get_owner(self, obj):
        owner = obj.owner
        return {
            "username": owner.username,
            "avatar": owner.userprofile.avatar.url if hasattr(owner, 'userprofile') and owner.userprofile.avatar else None
        } if owner else None
    
    def get_permissions(self, obj):
        user = self.context.get('request').user if self.context.get('request') else None
        if not user:
            return None
            
        try:
            permission = obj.permissions.get(user=user)
            return {
                'id': permission.id,
                'canEdit': permission.canEdit,         
                'canDelete': permission.canDelete,      
                'canAdd': permission.canAdd,         
                'canFinish': permission.canFinish,      
                'canAddMember': permission.canAddMember, 
                'canRemoveMember': permission.canRemoveMember
            }
        except:
            
            if obj.owner == user:
                return {
                    'id': None,
                    'canEdit': True,
                    'canDelete': True,
                    'canAdd': True,
                    'canFinish': True,
                    'canAddMember': True,   
                    'canRemoveMember': True
                }
            return None
    
    def create(self, validated_data):
        parentId = validated_data.pop('parentId', None)
        if parentId is None:
            
            parent = Project.objects.get(owner=self.context['request'].user, type="personal")
        else:
            parent = Project.objects.get(id=parentId)
            parent.type = 'project'
            parent.save()
        validated_data['parent'] = parent
        validated_data['owner'] = parent.owner
        project = super().create(validated_data)
        manager_ids = self.initial_data.get('manager_ids', [])
        project.managers.set(User.objects.filter(id__in=manager_ids))
        return project
    
    def update(self, instance, validated_data):
        manager_ids = self.initial_data.get('manager_ids')
        if manager_ids is not None:
            instance.managers.set(User.objects.filter(id__in=manager_ids))
        return super().update(instance, validated_data)

    def validate(self, data):
        if self.instance:
            if self.instance.type == 'task' and self.instance.endTime:
                current_time = timezone.now()
                new_progress = data.get('progress', self.instance.progress)
                if new_progress >= 100 and current_time > self.instance.endTime:
                    raise serializers.ValidationError("Không thể đánh dấu hoàn thành sau thời gian kết thúc.")
                
            if 'progress' in data:
                if data['progress'] >= 100 and not data.get('completeTime'):
                    data['completeTime'] = timezone.now()
                elif data['progress'] < 100:
                    data['completeTime'] = None
                    
        return data

class RecursiveProjectSerializer(serializers.ModelSerializer):
    """
    Serializer đệ quy cho model Project.
    
    Chức năng:
    - Chuyển đổi cấu trúc dự án thành dạng cây
    - Hiển thị thông tin cơ bản của dự án và các dự án con
    """
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = ['id', 'title', 'type', 'parent', 'children', 'color']

    def get_children(self, obj):
        """
        Lấy danh sách các dự án con được serialize đệ quy.
        
        Args:
            obj: Đối tượng Project hiện tại
            
        Returns:
            list: Danh sách các dự án con đã được serialize
        """
        return RecursiveProjectSerializer(obj.get_children(), many=True).data

class RecursiveProjectReportSerializer(ProjectSerializer):
    """
    Serializer đệ quy cho báo cáo dự án.
    
    Chức năng:
    - Tạo báo cáo chi tiết cho toàn bộ cây dự án
    - Bao gồm thông tin về managers và dự án con
    """
    children = serializers.SerializerMethodField()
    managers = serializers.SerializerMethodField()
    
    class Meta(ProjectSerializer.Meta):
        model = Project
        fields = ProjectSerializer.Meta.fields + ['children', 'managers']

    def get_children(self, obj):
        """
        Lấy danh sách báo cáo của các dự án con.
        
        Args:
            obj: Đối tượng Project hiện tại
            
        Returns:
            list: Danh sách báo cáo các dự án con
        """
        return RecursiveProjectReportSerializer(obj.get_children(), many=True, context=self.context).data

    def get_managers(self, obj):
        """
        Lấy thông tin của các quản lý dự án.
        
        Args:
            obj: Đối tượng Project hiện tại
            
        Returns:
            list: Danh sách thông tin cơ bản của các quản lý
        """
        return [{
            "id": manager.id,
            "username": manager.username,
            "avatar": manager.userprofile.avatar.url if hasattr(manager, 'userprofile') and manager.userprofile.avatar else None
        } for manager in obj.managers.all()]