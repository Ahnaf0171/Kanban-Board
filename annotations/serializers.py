import re
from rest_framework import serializers
from .models import Image, Annotation

MAX_IMAGE_SIZE_MB = 5
ALLOWED_IMAGE_TYPES = ('image/jpeg', 'image/png', 'image/webp')
HEX_COLOR_PATTERN = re.compile(r'^#(?:[0-9a-fA-F]{3}){1,2}$')


class AnnotationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Annotation
        fields = ('id', 'image', 'points', 'label', 'color', 'created_by', 'created_at')
        read_only_fields = ('id', 'created_by', 'created_at')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request is not None and 'image' in self.fields:
            self.fields['image'].queryset = Image.objects.filter(uploaded_by=request.user)

    def validate_points(self, value):
        if not isinstance(value, list) or len(value) < 3:
            raise serializers.ValidationError("A polygon needs at least 3 points.")
        for point in value:
            if not isinstance(point, dict) or 'x' not in point or 'y' not in point:
                raise serializers.ValidationError("Each point must be an object with 'x' and 'y'.")
            if not isinstance(point['x'], (int, float)) or not isinstance(point['y'], (int, float)):
                raise serializers.ValidationError("Point coordinates must be numbers.")
        return value

    def validate_color(self, value):
        if value and not HEX_COLOR_PATTERN.match(value):
            raise serializers.ValidationError("Color must be a valid hex code, e.g. '#FF0000' or '#F00'.")
        return value

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return Annotation.objects.create(**validated_data)


class ImageSerializer(serializers.ModelSerializer):
    annotations = AnnotationSerializer(many=True, read_only=True)

    class Meta:
        model = Image
        fields = ('id', 'file', 'order', 'uploaded_by', 'uploaded_at', 'annotations')
        read_only_fields = ('id', 'uploaded_by', 'uploaded_at')

    def validate_file(self, value):
        if value.content_type not in ALLOWED_IMAGE_TYPES:
            raise serializers.ValidationError("Only JPEG, PNG, or WEBP images are allowed.")
        if value.size > MAX_IMAGE_SIZE_MB * 1024 * 1024:
            raise serializers.ValidationError(f"Image must be under {MAX_IMAGE_SIZE_MB}MB.")
        return value

    def create(self, validated_data):
        validated_data['uploaded_by'] = self.context['request'].user
        return Image.objects.create(**validated_data)