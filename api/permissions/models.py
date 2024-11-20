from django.db import models
from django.contrib.auth.models import User
from api.project.models import Project

class Permissions(models.Model):
    """
    Model quản lý quyền hạn của người dùng trong dự án.
    
    Định nghĩa mối quan hệ giữa người dùng và dự án, xác định các hành động 
    mà người dùng được phép thực hiện trong phạm vi của dự án đó.
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='permissions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='permissions')
    
    canEdit = models.BooleanField(default=False)
    canDelete = models.BooleanField(default=False)
    canAdd = models.BooleanField(default=False)
    canFinish = models.BooleanField(default=False)
    
    canAddMember = models.BooleanField(default=False)
    canRemoveMember = models.BooleanField(default=False)

    class Meta:
        """
        Đảm bảo mỗi người dùng chỉ có một bộ quyền hạn cho mỗi dự án.
        """
        unique_together = ['project', 'user']