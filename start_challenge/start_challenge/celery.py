import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "start_challenge.settings")

app = Celery("start_challenge")
app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()
