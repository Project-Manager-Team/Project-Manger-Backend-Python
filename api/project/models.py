from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy
from mptt.models import MPTTModel, TreeForeignKey
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

class Project(MPTTModel):
    # Định nghĩa các lựa chọn cho loại project
    class ProjectType(models.TextChoices):
        PROJECT = "project", gettext_lazy("Project")
        TASK = "task", gettext_lazy("Task")
        PERSONAL = "personal", gettext_lazy("Personal")
    
    # Các trường thông tin của project
    title = models.CharField(max_length=100)
    progress = models.IntegerField(default=0)
    description = models.CharField(max_length=1000, blank=True, null=True)
    initTime = models.DateTimeField(auto_now_add=True)
    beginTime = models.DateTimeField(null=True)
    completeTime = models.DateTimeField(null=True, blank=True)
    endTime = models.DateTimeField(null=True)
    type = models.CharField(
        max_length=8,
        choices=ProjectType.choices,
        default=ProjectType.TASK,
        db_index=True
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='owned_projects',
        db_index=True
    )
    diffLevel = models.IntegerField(default=1, null=True)
    active = models.BooleanField(default=True)

    # Quan hệ ManyToMany với User để xác định managers
    managers = models.ManyToManyField(
        User,
        related_name='managed_projects',
        blank=True,
        db_index=True
    )

    # Quan hệ cây với chính nó để xác định project cha
    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        db_index=True
    )
    
    def is_completed(self):
        # Kiểm tra project đã hoàn thành hay chưa
        return self.progress == 100
    
    def update_progress(self, progress_value):
        # Cập nhật tiến độ của project
        self.progress = progress_value
        self.save()
        
    class MPTTMeta:
        # Thiết lập thứ tự chèn trong cây
        order_insertion_by = ['id']

    def __str__(self):
        # Chuỗi biểu diễn của project
        return f"{self.id} - {self.title} - {self.type}"

@receiver(m2m_changed, sender=Project.managers.through)
def add_permissions_for_manager(sender, instance, action, pk_set, **kwargs):
    if action == "post_add":
        from api.permissions.models import Permissions
        for user_id in pk_set:
            Permissions.objects.get_or_create(
                project=instance,
                user_id=user_id,
                defaults={
                    'canEdit': True,          # Cho phép chỉnh sửa
                    'canDelete': True,        # Cho phép xóa
                    'canAdd': True,           # Cho phép thêm project con
                    'canFinish': True,        # Cho phép đánh dấu hoàn thành
                    'canAddMember': False,    # Mặc định không cho phép thêm thành viên và tạo lời mời
                    'canRemoveMember': False  # Mặc định không cho phép xóa thành viên
                }
            )
