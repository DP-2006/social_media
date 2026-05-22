
# import os
# from celery import Celery

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# app = Celery('core')
# app.config_from_object('django.conf:settings', namespace='CELERY')
# app.autodiscover_tasks()
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('core')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'delete-expired-stories': {
        'task': 'apps.stories.tasks.delete_expired_stories',
        'schedule': crontab(minute=0, hour='*'),  #
        'args': (), 
        'kwargs': {},  
    },
    
    'cleanup-expired-otp': {
        'task': 'your_otp_app.tasks.cleanup_expired_otp',  
        'schedule': crontab(minute='*/5'),  
    },
}

app.conf.timezone = 'UTC'  

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')