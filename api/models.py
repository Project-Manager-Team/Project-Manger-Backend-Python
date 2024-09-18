from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User


# Create model Project
class Project(models.Model):
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=1000)
    time_init = models.DateTimeField(auto_now_add=True)
    time_start = models.DateTimeField()
    time_end = models.DateTimeField()
    type = models.BooleanField(default=False)  # False: Task , True: Project

    # Create link to User Model
    owner_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )

    # Create link to Project_Model
    owner_project = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )

    def __str__(self):
        return f"{self.id} - {self.title} - {"Project" if type else "Task"}"
