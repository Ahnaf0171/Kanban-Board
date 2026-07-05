from rest_framework import viewsets, permissions, parsers
from rest_framework.pagination import PageNumberPagination
from .models import Image, Annotation
from .serializers import ImageSerializer, AnnotationSerializer


class ImagePagination(PageNumberPagination):
    page_size = 30


class ImageViewSet(viewsets.ModelViewSet):
    serializer_class = ImageSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]
    pagination_class = ImagePagination
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_queryset(self):
        return Image.objects.filter(
            uploaded_by=self.request.user
        ).prefetch_related('annotations').order_by('order', 'uploaded_at')


class AnnotationViewSet(viewsets.ModelViewSet):
    serializer_class = AnnotationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Annotation.objects.filter(
            created_by=self.request.user
        ).select_related('image')