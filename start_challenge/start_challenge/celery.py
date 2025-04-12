import os
from celery import Celery
from . import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "start_challenge.settings")

app = Celery("start_challenge")
app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()

app.conf.broker_transport_options = {
    'region': os.environ.get('AWS_DEFAULT_REGION'),
    'visibility_timeout': 3600,
}

app.conf.broker_connection_retry_on_startup = True

app.conf.broker_transport_options = settings.CELERY_BROKER_TRANSPORT_OPTIONS
