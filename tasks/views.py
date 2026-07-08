from datetime import datetime
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from .models import Task, Tag
from .serializers import TaskSerializer, TagSerializer, TaskReorderSerializer
from django.db import transaction
from django.db.models import F


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
        serializer = TaskReorderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_status = serializer.validated_data['status']
        new_order = serializer.validated_data['order']
        old_status = task.status
        old_order = task.order

        with transaction.atomic():
            base_qs = Task.objects.select_for_update().filter(user=request.user)
            if old_status == new_status:
                if new_order > old_order:
                    base_qs.filter(
                        status=new_status,
                        order__gt=old_order,
                        order__lte=new_order,
                    ).exclude(pk=task.pk).update(order=F('order') - 1)
                elif new_order < old_order:
                    base_qs.filter(
                        status=new_status,
                        order__gte=new_order,
                        order__lt=old_order,
                    ).exclude(pk=task.pk).update(order=F('order') + 1)
            else:
                base_qs.filter(
                    status=old_status,
                    order__gt=old_order,
                ).update(order=F('order') - 1)
                base_qs.filter(
                    status=new_status,
                    order__gte=new_order,
                ).update(order=F('order') + 1)

            task.status = new_status
            task.order = new_order
            task.save(update_fields=['status', 'order', 'updated_at'])

        return Response(TaskSerializer(task, context={'request': request}).data)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticated]