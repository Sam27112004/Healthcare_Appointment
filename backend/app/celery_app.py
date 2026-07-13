from celery import Celery
from celery.schedules import crontab
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
    task_routes={
        "app.ai.tasks.*": {"queue": "ai"},
        "app.notifications.tasks.*": {"queue": "email"},
        "app.calendar.tasks.*": {"queue": "calendar"}
    },
    
    # Beat schedule
    beat_schedule={
        "cleanup-expired-holds": {
            "task": "app.appointment.tasks.cleanup_expired_holds",
            "schedule": 60.0,
        },
        "send-appointment-reminders": {
            "task": "app.notifications.tasks.send_appointment_reminders_task",
            "schedule": crontab(hour=8, minute=0),
        },
        "send-medication-reminders": {
            "task": "app.notifications.tasks.send_medication_reminders_task",
            "schedule": crontab(minute="*/30"),
        },
        "retry-failed-notifications": {
            "task": "app.notifications.tasks.retry_failed_notifications_task",
            "schedule": 300.0,
        },
    }
)

# Autodiscover tasks
celery_app.autodiscover_tasks([
    "app.ai",
    "app.appointment",
    "app.notifications",
    "app.calendar"
])
