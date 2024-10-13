
from django.urls import path, include
from rest_framework import routers
router = routers.DefaultRouter()
from . import views
router.register(r'', views.PersonalProjectViewSet,
                basename='personal-project')

urlpatterns = [
    path('', include(router.urls))
]