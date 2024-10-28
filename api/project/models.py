from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy
from mptt.models import MPTTModel, TreeForeignKey

class Project(MPTTModel):
    class ProjectType(models.TextChoices):
        PROJECT = "project", gettext_lazy("Project")
        TASK = "task", gettext_lazy("Task")
        PERSONAL = "personal", gettext_lazy("Personal")
    
    title = models.CharField(max_length=100)
    progress = models.IntegerField(default=0)
    description = models.CharField(max_length=1000, blank=True, null=True)
    time_init = models.DateTimeField(auto_now_add=True)
    time_start = models.DateTimeField(null=True)
    time_completed = models.DateTimeField(null=True, blank=True)
    time_end = models.DateTimeField(null=True)
    type = models.CharField(
        max_length=8,
        choices=ProjectType.choices,
        default=ProjectType.TASK,
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='owned_projects',
        db_index=True
    )
    difficulty_level = models.IntegerField(default=1, null=True)
    active = models.BooleanField(default=True)

    manager = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='manager'
    )

    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        db_index=True
    )
    
    level = models.IntegerField(default=0)
    
    
    def is_completed(self):
        return self.progress == 100
    
    def update_progress(self, progress_value):
        self.progress = progress_value
        self.save()
        
    class MPTTMeta:
        order_insertion_by = ['id']

    def __str__(self):
        return f"{self.id} - {self.title} - {self.type}"
