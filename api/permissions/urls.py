from rest_framework import routers
from .views import PermissionsViewSet

router = routers.DefaultRouter()
router.register(r'', PermissionsViewSet)

urlpatterns = router.urls
