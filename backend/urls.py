from django.contrib import admin
from django.urls import path, include
from api import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/", include("api.urls")),
    path('ws/', views.send_notification, name='send_notification'),
]
