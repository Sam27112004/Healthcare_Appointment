from celery import Celery
from app.config import settings

celery_app = Celery(
    "hospital_tasks",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    # Configure retry defaults
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)

# Autodiscover tasks
celery_app.autodiscover_tasks([
    "app.ai",
    "app.appointment",
    "app.notifications"
])
