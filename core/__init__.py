from .celery import app as celery_app

# Expose the Celery app as a module-level variable so `celery -A core` works.
__all__ = ("celery_app",)

