from django.db import models
from django.conf import settings


class Image(models.Model):
    file = models.ImageField(upload_to='annotation_images/')
    order = models.PositiveIntegerField(default=0)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='images'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']  

    def __str__(self):
        return f"Image #{self.id} by {self.uploaded_by.email}"


class Annotation(models.Model):
    image = models.ForeignKey(
        Image,
        on_delete=models.CASCADE,
        related_name='annotations'
    )

    points = models.JSONField()
    label = models.CharField(max_length=100, blank=True, null=True)
    color = models.CharField(max_length=20, blank=True, null=True)  

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='annotations'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Annotation #{self.id} on Image #{self.image.id}"