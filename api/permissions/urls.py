from rest_framework import routers
from .views import PermissionsViewSet

router = routers.DefaultRouter()
router.register(r'permissions', PermissionsViewSet)

urlpatterns = router.urls
