"""
Cấu hình routing cho ứng dụng project.

Định nghĩa:
- Router mặc định cho PersonalProjectViewSet
- Các đường dẫn URL của API liên quan đến dự án
"""

from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'', views.PersonalProjectViewSet, basename='personal-project')

urlpatterns = [
    path('', include(router.urls)),
]