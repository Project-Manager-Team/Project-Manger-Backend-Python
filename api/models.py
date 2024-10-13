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
    description = models.CharField(max_length=1000)
    time_init = models.DateTimeField(auto_now_add=True)
    time_start = models.DateTimeField(null=True)
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
        related_name='owner'
    )

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
        related_name='children'
    )

    level = models.IntegerField(default=0)

    class MPTTMeta:
        order_insertion_by = ['title']

    def __str__(self):
        return f"{self.id} - {self.title} - {self.type}"


class Invitation (models.Model):
    title = models.CharField(max_length=50)
    context = models.CharField(max_length=200)
    status = models.BooleanField(default=False)

    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        related_name='receiver',
        default=1
    )

    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        related_name='sender',
        default=1
    )

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        blank=False,
        null=True,
        related_name='project'
    )
