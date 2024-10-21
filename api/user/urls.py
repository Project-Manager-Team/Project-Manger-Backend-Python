from django.urls import path

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import UserRegister, UserDetail, ChangePasswordView
urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("register/", UserRegister.as_view(), name=""),
    path("detail/", UserDetail.as_view(), name=""),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
]