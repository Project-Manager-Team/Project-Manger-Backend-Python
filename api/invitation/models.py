from datetime import timedelta
from django.db import models
from django.contrib.auth.models import User
from api.project.models import Project
from django.utils import timezone

class Invitation(models.Model):
    """
    Model quản lý lời mời tham gia dự án.
    
    Một lời mời được gửi từ người dùng này (sender) đến người dùng khác (receiver)
    để tham gia vào một dự án cụ thể. Bao gồm tiêu đề, nội dung, thời hạn,
    và trạng thái chấp nhận lời mời.
    """
    title = models.CharField(max_length=50)
    content = models.CharField(max_length=200)
    sendTime = models.DateTimeField(auto_now_add=True, null=True)
    duration = models.DurationField(default=timedelta())
    status = models.BooleanField(null=True, blank=True)

    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        related_name='received_invitations'
    )

    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        related_name='sent_invitations'
    )

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        blank=False,
        null=True,
        related_name='invitations'
    )

    def accept(self):
        """
        Chấp nhận lời mời và thêm người nhận vào dự án.
        
        Phương thức này:
        1. Thêm người nhận làm quản lý vào dự án liên quan
        2. Đặt trạng thái lời mời thành True (đã chấp nhận)
        3. Lưu các thay đổi vào cơ sở dữ liệu
        """
        self.project.managers.add(self.receiver)
        self.status = True
        self.save()
