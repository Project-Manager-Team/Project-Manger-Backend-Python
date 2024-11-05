from django.db import models
from django.contrib.auth.models import User
from api.project.models import Project

class Permissions(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='permissions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='permissions')
    canEdit = models.BooleanField(default=False)
    canDelete = models.BooleanField(default=False)
    canAdd = models.BooleanField(default=False)
    canFinish = models.BooleanField(default=False)

    class Meta:
        unique_together = ['project', 'user']