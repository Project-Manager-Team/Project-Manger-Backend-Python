from django.db import models
from django.contrib.auth.models import User
from api.project.models import Project

class Permissions(models.Model):
    # Quan hệ với Project và User
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='permissions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='permissions')
    
    # Các quyền cơ bản
    canEdit = models.BooleanField(default=False)     # Quyền chỉnh sửa project
    canDelete = models.BooleanField(default=False)   # Quyền xóa project
    canAdd = models.BooleanField(default=False)      # Quyền thêm project con
    canFinish = models.BooleanField(default=False)   # Quyền đánh dấu hoàn thành
    
    # Các quyền quản lý thành viên
    canAddMember = models.BooleanField(default=False)    # Quyền thêm thành viên và tạo lời mời
    canRemoveMember = models.BooleanField(default=False) # Quyền xóa thành viên khỏi project

    class Meta:
        # Đảm bảo mỗi user chỉ có một bản ghi permission cho mỗi project
        unique_together = ['project', 'user']