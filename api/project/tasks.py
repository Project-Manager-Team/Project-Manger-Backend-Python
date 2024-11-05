from celery import shared_task
from django.shortcuts import get_object_or_404
from django.db.models import Avg
from .models import Project

# Định nghĩa một tác vụ dùng Celery để cập nhật tiến độ của project cha
@shared_task
def update_parent_progress(projectId):
    # Lấy project dựa trên ID
    project = Project.objects.select_related('parent').prefetch_related('children').filter(id=projectId).first()
    # Lặp lại cho đến khi không còn project cha
    while project:
        # Lấy các project con trực tiếp
        children = project.get_children()
        if children.exists():
            # Tính trung bình tiến độ của các project con
            avg_progress = children.aggregate(Avg('progress'))['progress__avg']
            # Cập nhật tiến độ của project hiện tại
            project.update_progress(avg_progress)
        # Di chuyển lên project cha
        project = project.parent