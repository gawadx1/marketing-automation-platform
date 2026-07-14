from celery import Celery
from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "marketing_worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.workers.tasks"],
)

celery_app.conf.update(
    task_serializer=settings.CELERY_TASK_SERIALIZER,
    accept_content=settings.CELERY_ACCEPT_CONTENT,
    result_serializer=settings.CELERY_RESULT_SERIALIZER,
    timezone=settings.CELERY_TIMEZONE,
    enable_utc=settings.CELERY_ENABLE_UTC,
    task_track_started=settings.CELERY_TASK_TRACK_STARTED,
    task_time_limit=settings.CELERY_TASK_TIME_LIMIT,
    task_soft_time_limit=settings.CELERY_TASK_SOFT_TIME_LIMIT,
    worker_max_tasks_per_child=settings.CELERY_WORKER_MAX_TASKS_PER_CHILD,
    worker_prefetch_multiplier=settings.CELERY_WORKER_PREFETCH_MULTIPLIER,
    task_acks_late=settings.CELERY_TASK_ACKS_LATE,
    task_reject_on_worker_lost=True,
    worker_send_task_events=True,
    task_send_sent_event=True,
    result_expires=3600 * 24 * 7,
    broker_connection_retry_on_startup=True,
    broker_connection_max_retries=10,
    beat_schedule={
        "fetch-campaign-metrics-every-minute": {
            "task": "app.workers.tasks.fetch_all_campaign_metrics",
            "schedule": 60.0,
            "options": {"queue": "default", "retry": True},
        },
        "fetch-contacts-every-minute": {
            "task": "app.workers.tasks.fetch_all_contacts",
            "schedule": 60.0,
            "options": {"queue": "default"},
        },
        "generate-hourly-report": {
            "task": "app.workers.tasks.generate_daily_report",
            "schedule": 3600.0,
            "options": {"queue": "default"},
        },
        "cleanup-old-logs": {
            "task": "app.workers.tasks.cleanup_old_logs",
            "schedule": 86400.0,
            "options": {"queue": "maintenance"},
        },
    },
    task_queues={
        "default": {"exchange": "default", "routing_key": "default"},
        "maintenance": {"exchange": "maintenance", "routing_key": "maintenance"},
        "email": {"exchange": "email", "routing_key": "email"},
    },
    task_routes={
        "app.workers.tasks.cleanup_old_logs": {"queue": "maintenance"},
        "app.workers.tasks.send_email_task": {"queue": "email"},
        "app.workers.tasks.notify_sales_team": {"queue": "email"},
    },
)
