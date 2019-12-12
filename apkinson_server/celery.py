from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery import shared_task

from apkinson_server import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apkinson_server.settings')

# app = Celery('apkinson_server')
app = Celery('apkinson_server', backend='redis://localhost', broker='redis://guest@localhost//')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
# app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
# app.autodiscover_tasks(packages=['appkinson_server.apkinson_mobile.ApkinsonMobileConfig',
# 'apkinson_server.apkinson_server'], force=True)


@shared_task()
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
