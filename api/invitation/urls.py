from django.urls import path, include
from .views import InvitationViewSet
from rest_framework import routers

router = routers.DefaultRouter()
router.register('', InvitationViewSet)

urlpatterns = [
    path("", include(router.urls))
]
