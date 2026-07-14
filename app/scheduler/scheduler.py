from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from app.core.celery_app import celery_app
from loguru import logger

scheduler = AsyncIOScheduler(
    job_defaults={
        "coalesce": True,
        "max_instances": 1,
        "misfire_grace_time": 30,
    }
)


def start_scheduler():
    jobs = [
        {
            "id": "fetch_campaign_metrics",
            "name": "Fetch campaign metrics every minute",
            "trigger": IntervalTrigger(seconds=60),
            "func": trigger_celery_task,
            "args": ["app.workers.tasks.fetch_all_campaign_metrics"],
            "misfire_grace_time": 30,
        },
        {
            "id": "fetch_contacts",
            "name": "Fetch contacts every minute",
            "trigger": IntervalTrigger(seconds=60),
            "func": trigger_celery_task,
            "args": ["app.workers.tasks.fetch_all_contacts"],
            "misfire_grace_time": 30,
        },
        {
            "id": "generate_report",
            "name": "Generate daily report hourly",
            "trigger": IntervalTrigger(hours=1),
            "func": trigger_celery_task,
            "args": ["app.workers.tasks.generate_daily_report"],
            "misfire_grace_time": 300,
        },
        {
            "id": "cleanup_logs",
            "name": "Cleanup old logs daily at 2am",
            "trigger": CronTrigger(hour=2, minute=0),
            "func": trigger_celery_task,
            "args": ["app.workers.tasks.cleanup_old_logs"],
            "misfire_grace_time": 3600,
        },
        {
            "id": "heartbeat",
            "name": "Heartbeat check every 30 seconds",
            "trigger": IntervalTrigger(seconds=30),
            "func": trigger_celery_task,
            "args": ["app.workers.tasks.test_task"],
            "misfire_grace_time": 15,
        },
    ]

    for job in jobs:
        scheduler.add_job(
            id=job["id"],
            func=job["func"],
            trigger=job["trigger"],
            args=job["args"],
            name=job["name"],
            replace_existing=True,
            misfire_grace_time=job.get("misfire_grace_time", 30),
        )
        logger.info(f"Scheduler job registered: {job['name']} ({job['id']})")

    scheduler.start()
    logger.info(f"APScheduler started with {len(jobs)} jobs")


def trigger_celery_task(task_path: str):
    logger.debug(f"Triggering Celery task: {task_path}")
    celery_app.send_task(task_path)


def stop_scheduler():
    try:
        scheduler.shutdown(wait=False)
        logger.info("APScheduler stopped")
    except Exception as e:
        logger.error(f"Error stopping scheduler: {e}")
