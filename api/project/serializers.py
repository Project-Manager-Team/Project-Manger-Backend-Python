from rest_framework import serializers
from ..models import Project
from django.contrib.auth.models import User
from django.utils import timezone
from api.permissions.serializers import PermissionsSerializer

class ProjectSerializer(serializers.ModelSerializer):
    # Trường để nhận ID của project cha
    parentId = serializers.IntegerField(required=False, allow_null=True)
    # Trường để hiển thị số lượng managers
    managersCount = serializers.SerializerMethodField()
    # Trường để hiển thị thông tin owner
    owner = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = ['id', 'title', 'description', 'beginTime', 'completeTime',
                  'endTime', 'type', 'managersCount', 'owner', 'parentId', 'progress', 
                  'diffLevel', 'permissions']  # Thay đổi managers thành managers_count và loại bỏ managers_permissions
    
    def get_managersCount(self, obj):
        # Trả về số lượng managers của project
        return obj.managers.count()
    
    def get_owner(self, obj):
        # Lấy thông tin owner của project
        owner = obj.owner
        return {
            "username": owner.username,
            "avatar": owner.userprofile.avatar.url if hasattr(owner, 'userprofile') and owner.userprofile.avatar else None
        } if owner else None
    
    def get_permissions(self, obj):
        # Lấy quyền của user hiện tại đối với project này
        user = self.context['request'].user
        try:
            permission = obj.permissions.get(user=user)
            return {
                'id': permission.id,
                'canEdit': permission.canEdit,           # Quyền chỉnh sửa
                'canDelete': permission.canDelete,       # Quyền xóa
                'canAdd': permission.canAdd,             # Quyền thêm
                'canFinish': permission.canFinish,       # Quyền hoàn thành
                'canAddMember': permission.canAddMember,     # Quyền thêm thành viên
                'canRemoveMember': permission.canRemoveMember # Quyền xóa thành viên
            }
        except:
            # Nếu là owner, trả về tất cả quyền
            if obj.owner == user:
                return {
                    'id': None,
                    'canEdit': True,
                    'canDelete': True,
                    'canAdd': True,
                    'canFinish': True,
                    'canAddMember': True,     # Owner luôn có quyền quản lý thành viên
                    'canRemoveMember': True
                }
            return None
    
    def create(self, validated_data):
        # Xử lý dữ liệu khi tạo mới project
        parentId = validated_data.pop('parentId', None)
        if parentId is None:
            # Nếu không có parentId, project cha là personal project của user
            parent = Project.objects.get(owner=self.context['request'].user, type="personal")
        else:
            # Nếu có parentId, lấy project cha tương ứng
            parent = Project.objects.get(id=parentId)
            # Chuyển loại project cha thành 'project' nếu cần
            parent.type = 'project'
            parent.save()
        # Gán project cha và chủ sở hữu của project cha
        validated_data['parent'] = parent
        validated_data['owner'] = parent.owner
        # Tạo project mới
        project = super().create(validated_data)
        # Thiết lập managers cho project
        manager_ids = self.initial_data.get('manager_ids', [])
        project.managers.set(User.objects.filter(id__in=manager_ids))
        return project
    
    def update(self, instance, validated_data):
        # Xử lý dữ liệu khi cập nhật project
        manager_ids = self.initial_data.get('manager_ids')
        if manager_ids is not None:
            # Cập nhật danh sách managers
            instance.managers.set(User.objects.filter(id__in=manager_ids))
        return super().update(instance, validated_data)

    def validate(self, data):
        # Kiểm tra dữ liệu đầu vào
        request = self.context.get('request')
        if self.instance:
            # Kiểm tra nếu project là 'task' và có 'endTime'
            if self.instance.type == 'task' and self.instance.endTime:
                current_time = timezone.now()
                new_progress = data.get('progress', self.instance.progress)
                # Không cho phép đánh dấu hoàn thành sau 'endTime'
                if new_progress >= 100 and current_time > self.instance.endTime:
                    raise serializers.ValidationError("Không thể đánh dấu hoàn thành sau thời gian kết thúc.")
        return data

# If there's a nested serializer or related field that needs 'canFinish', update accordingly



