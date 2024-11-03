from django.urls import path
from django.urls.conf import include
from rest_framework.routers import DefaultRouter
from .views import UserProfileViewSet, UserViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import UserRegister

router = DefaultRouter()
router.register(r'profile', UserProfileViewSet)
router.register(r'', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)), 
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', UserRegister.as_view(), name='user_register'),
]
