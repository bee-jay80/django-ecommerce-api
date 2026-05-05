import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

app = Celery("core")

# Load settings from Django
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks in all apps
app.autodiscover_tasks()