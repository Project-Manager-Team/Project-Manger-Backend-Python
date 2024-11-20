from celery import shared_task
from django.shortcuts import get_object_or_404
from django.db.models import Avg
from .models import Project

# Định nghĩa một tác vụ dùng Celery để cập nhật tiến độ của project cha
@shared_task
def update_parent_progress(projectId):
    """
    Tác vụ Celery để cập nhật tiến độ của dự án cha.
    - Tính toán tiến độ trung bình từ các dự án con
    - Cập nhật ngược lên cây dự án cho đến gốc
    
    Tham số:
        projectId: ID của dự án cần cập nhật
    """
    project = Project.objects.select_related('parent').prefetch_related('children').filter(id=projectId).first()
    while project:
        children = project.get_children()
        if children.exists():
            avg_progress = children.aggregate(Avg('progress'))['progress__avg']
            project.update_progress(avg_progress)
        project = project.parent