from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy
from mptt.models import MPTTModel, TreeForeignKey
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

class Project(MPTTModel):
    """
    Model quản lý thông tin dự án theo cấu trúc cây.
    
    Các trường chính:
    - title: Tên dự án
    - progress: Tiến độ (0-100)
    - type: Loại (project/task/personal) 
    - owner: Người tạo dự án
    - managers: Danh sách người quản lý
    - parent: Dự án cha
    """
    class ProjectType(models.TextChoices):
        PROJECT = "project", gettext_lazy("Project")
        TASK = "task", gettext_lazy("Task")
        PERSONAL = "personal", gettext_lazy("Personal")
    
    title = models.CharField(max_length=100)
    progress = models.IntegerField(default=0)
    description = models.CharField(max_length=1000, blank=True, null=True)
    initTime = models.DateTimeField(auto_now_add=True)
    beginTime = models.DateTimeField(null=True)
    completeTime = models.DateTimeField(null=True, blank=True)
    endTime = models.DateTimeField(null=True)
    color = models.CharField(max_length=20, null=True, blank=True)
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

    managers = models.ManyToManyField(
        User,
        related_name='managed_projects',
        blank=True,
        db_index=True
    )

    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        db_index=True
    )
    
    def is_completed(self):
        """
        Kiểm tra trạng thái hoàn thành của dự án.
        Returns:
            bool: True nếu dự án đã hoàn thành (progress = 100)
        """
        return self.progress == 100
    
    def update_progress(self, progress_value):
        self.progress = progress_value
        self.save()
        
    class MPTTMeta:
        order_insertion_by = ['id']

    def __str__(self):
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
                    'canEdit': True,          
                    'canDelete': True,       
                    'canAdd': True,          
                    'canFinish': True,    
                    'canAddMember': False,    
                    'canRemoveMember': False  
                }
            )
