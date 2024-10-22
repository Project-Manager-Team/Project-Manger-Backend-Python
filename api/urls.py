
from django.urls import path, include
from rest_framework import routers

urlpatterns = [
    path('user/', include('api.user.urls')),
    path('project/', include('api.project.urls')),
    path('invitation/', include('api.invitation.urls')),
]
