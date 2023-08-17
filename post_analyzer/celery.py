from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'post_analyzer.settings')

app = Celery('post_analyzer')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.broker_connection_retry_on_startup = True



# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

