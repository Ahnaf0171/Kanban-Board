from django.apps import AppConfig


class AnnotationsConfig(AppConfig):
    name = 'annotations'

    def ready(self):
        from . import signals  