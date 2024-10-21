from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)
urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/", include("api.urls")),
    path("install/", SpectacularAPIView.as_view(), name="schema"),
    path("install/swagger-ui/", SpectacularSwaggerView.as_view(url_name="schema")),
]
