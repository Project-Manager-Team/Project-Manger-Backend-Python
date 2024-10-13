from django.urls import path
from .views import InvitationViewSet


urlpatterns = [
    path('', InvitationViewSet.as_view())
]
