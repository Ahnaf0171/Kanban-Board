from rest_framework.routers import DefaultRouter
from .views import ImageViewSet, AnnotationViewSet

router = DefaultRouter()
router.register('images', ImageViewSet, basename='image')
router.register('annotations', AnnotationViewSet, basename='annotation')

urlpatterns = router.urls