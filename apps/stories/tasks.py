# apps/stories/tasks.py

from celery import shared_task
from django.utils import timezone
from django.core.management import call_command
from .models import Story

@shared_task
def delete_expired_stories():
    expired_stories = Story.objects.filter(expires_at__lte=timezone.now())
    count = expired_stories.count()
    
    if count > 0:
        expired_stories.delete()
        return f" {count} expired stories deleted successfully"
    return " No expired stories found"


@shared_task
def check_and_delete_expired_stories():
    from django.utils import timezone
    
    now = timezone.now()
    expired_stories = Story.objects.filter(expires_at__lte=now)
    count = expired_stories.count()
    
    if count > 0:
        story_ids = list(expired_stories.values_list('id', flat=True))
        expired_stories.delete()
        
        return {
            'status': 'success',
            'deleted_count': count,
            'deleted_story_ids': story_ids,
            'time': str(now)
        }
    
    return {
        'status': 'no_expired',
        'deleted_count': 0,
        'time': str(now)
    }