from celery import shared_task
from django.shortcuts import get_object_or_404
from django.db.models import Avg
from .models import Project

@shared_task
def update_parent_progress(projectId):
    project = Project.objects.select_related('parent').prefetch_related('children').filter(id=projectId).first()
    while project:
        children = project.get_children()
        if children.exists():
            avg_progress = children.aggregate(Avg('progress'))['progress__avg']
            project.update_progress(avg_progress)
        project = project.parent