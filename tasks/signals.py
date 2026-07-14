from django.db.models.signals import m2m_changed, pre_delete, post_delete
from django.dispatch import receiver
from .models import Task, Tag


def _delete_unused_tags(tag_ids):
    if tag_ids:
        Tag.objects.filter(pk__in=tag_ids, tasks__isnull=True).delete()


@receiver(m2m_changed, sender=Task.tags.through)
def cleanup_tags_on_m2m_change(sender, instance, action, pk_set, **kwargs):
    if action == 'pre_clear':
        instance._prior_tag_ids = list(instance.tags.values_list('pk', flat=True))
    elif action == 'post_remove':
        _delete_unused_tags(pk_set)
    elif action == 'post_clear':
        _delete_unused_tags(getattr(instance, '_prior_tag_ids', []))


@receiver(pre_delete, sender=Task)
def capture_tags_before_task_delete(sender, instance, **kwargs):
    instance._prior_tag_ids = list(instance.tags.values_list('pk', flat=True))


@receiver(post_delete, sender=Task)
def cleanup_tags_after_task_delete(sender, instance, **kwargs):
    _delete_unused_tags(getattr(instance, '_prior_tag_ids', []))