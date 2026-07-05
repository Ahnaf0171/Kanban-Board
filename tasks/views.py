from datetime import datetime
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from .models import Task, Tag
from .serializers import TaskSerializer, TagSerializer, TaskReorderSerializer


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Task.objects.filter(user=self.request.user).prefetch_related('tags')
        due_date = self.request.query_params.get('due_date')
        if due_date:
            try:
                parsed = datetime.strptime(due_date, '%Y-%m-%d').date()
            except ValueError:
                raise ValidationError({'due_date': 'Invalid date format. Use YYYY-MM-DD.'})
            qs = qs.filter(due_date=parsed)
        return qs

    @action(detail=True, methods=['patch'], url_path='reorder')
    def reorder(self, request, pk=None):
        task = self.get_object()
        serializer = TaskReorderSerializer(task, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(TaskSerializer(task, context={'request': request}).data)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticated]