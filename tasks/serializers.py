from rest_framework import serializers
from django.utils import timezone
from .models import Task, Tag

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color')
        read_only_fields = ('id',)

class TaskSerializer(serializers.ModelSerializer):
    tags = serializers.ListField(
        child=serializers.CharField(max_length=50, allow_blank=False),
        required=False,
        write_only=True,
        help_text="List of tag names, e.g. ['urgent', 'backend']"
    )
    tags_display = TagSerializer(source='tags', many=True, read_only=True)

    class Meta:
        model = Task
        fields = (
            'id', 'title', 'description', 'status', 'priority',
            'due_date', 'tags', 'tags_display', 'order',
            'created_at', 'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate_title(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Title cannot be empty.")
        return value

    def validate_due_date(self, value):
        if self.instance is None and value < timezone.localdate():
            raise serializers.ValidationError("Due date cannot be in the past.")
        return value

    def validate_tags(self, value):
        cleaned = []
        for name in value:
            name = name.strip().lower()
            if not name:
                raise serializers.ValidationError("Tag names cannot be blank.")
            if name not in cleaned:
                cleaned.append(name)
        return cleaned

    def _sync_tags(self, task, tag_names):
        tags = [Tag.objects.get_or_create(name=name)[0] for name in tag_names]
        task.tags.set(tags)

    def create(self, validated_data):
        tag_names = validated_data.pop('tags', [])
        task = Task.objects.create(user=self.context['request'].user, **validated_data)
        if tag_names:
            self._sync_tags(task, tag_names)
        return task

    def update(self, instance, validated_data):
        tag_names = validated_data.pop('tags', None)
        instance = super().update(instance, validated_data)
        if tag_names is not None:
            self._sync_tags(instance, tag_names)
        return instance

class TaskReorderSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Task.STATUS_CHOICES)
    order = serializers.IntegerField(min_value=0)
