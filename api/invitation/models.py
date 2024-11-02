from datetime import timedelta
from django.db import models
from django.contrib.auth.models import User
from api.project.models import Project
from django.utils import timezone


class Invitation(models.Model):
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
        self.project.managers.add(self.receiver)
        self.status = True
        self.save()
