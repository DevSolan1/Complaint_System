from rest_framework.routers import DefaultRouter

from .api_views import ComplaintViewSet

router = DefaultRouter()
router.register("complaints", ComplaintViewSet, basename="api-complaints")

urlpatterns = router.urls
