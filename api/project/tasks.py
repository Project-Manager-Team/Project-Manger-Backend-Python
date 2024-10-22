from celery import shared_task
from django.shortcuts import get_object_or_404
from django.db.models import Avg
from .models import Project

@shared_task
def update_parent_progress(project_id):
    project = get_object_or_404(Project, id=project_id)
    
    while project:
        childrens = project.get_children()
        
        if childrens.exists():
            avg_progress = childrens.aggregate(Avg('progress'))['progress__avg']
            project.progress = avg_progress
            project.save()
        project = project.parent
