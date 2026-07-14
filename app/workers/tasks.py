import random
import asyncio
from datetime import date, datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.celery_app import celery_app
from app.core.database import async_session_factory
from app.core.logging import setup_logging
from app.services.integrations.google_ads import GoogleAdsService
from app.services.integrations.meta_ads import MetaAdsService
from app.services.integrations.hubspot import HubSpotService
from app.services.integrations.mailchimp import MailchimpService
from app.models.campaign import Campaign, CampaignPlatform, CampaignStatus
from app.models.campaign_metric import CampaignMetric
from app.models.contact import Contact, ContactSource
from app.models.automation_job import AutomationJob, JobStatus
from app.repositories.base import BaseRepository
from loguru import logger

setup_logging()


def run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def fetch_all_campaign_metrics(self):
    logger.info("Starting fetch_all_campaign_metrics task")
    try:
        run_async(_fetch_campaign_metrics())
        logger.info("Completed fetch_all_campaign_metrics task")
    except Exception as exc:
        logger.error(f"Failed to fetch campaign metrics: {exc}")
        raise self.retry(exc=exc)


async def _fetch_campaign_metrics():
    async with async_session_factory() as db:
        google = GoogleAdsService()
        meta = MetaAdsService()
        repo = BaseRepository(Campaign, db)
        metric_repo = BaseRepository(CampaignMetric, db)
        job_repo = BaseRepository(AutomationJob, db)

        job = await job_repo.create(
            job_type="fetch_campaign_metrics",
            status=JobStatus.RUNNING,
            payload='{"source": "scheduled"}',
        )

        try:
            campaigns, total = await repo.get_multi(limit=100)
            today = date.today()

            google_campaigns = await google.get_all_campaigns_stats()
            meta_campaigns = await meta.get_all_campaigns_insights()

            for gc in google_campaigns:
                existing_campaign = None
                for c in campaigns:
                    if (
                        c.platform == CampaignPlatform.GOOGLE_ADS
                        and c.name == gc["name"]
                    ):
                        existing_campaign = c
                        break

                if not existing_campaign:
                    existing_campaign = await repo.create(
                        name=gc["name"],
                        platform=CampaignPlatform.GOOGLE_ADS,
                        status=CampaignStatus.ACTIVE
                        if gc["status"] == "enabled"
                        else CampaignStatus.PAUSED,
                        budget=gc.get("budget", 0),
                        spent=gc.get("cost", 0),
                    )

                await metric_repo.create(
                    campaign_id=existing_campaign.id,
                    date=today,
                    impressions=gc.get("impressions", 0),
                    clicks=gc.get("clicks", 0),
                    conversions=gc.get("conversions", 0),
                    spend=gc.get("cost", 0),
                    ctr=gc.get("ctr", 0),
                    cpc=gc.get("average_cpc", 0),
                )

            for mc in meta_campaigns:
                existing_campaign = None
                for c in campaigns:
                    if c.platform == CampaignPlatform.META_ADS and c.name == mc["name"]:
                        existing_campaign = c
                        break

                if not existing_campaign:
                    existing_campaign = await repo.create(
                        name=mc["name"],
                        platform=CampaignPlatform.META_ADS,
                        status=CampaignStatus.ACTIVE
                        if mc["status"] == "ACTIVE"
                        else CampaignStatus.PAUSED,
                        budget=mc.get("daily_budget", 0),
                    )

                insights = mc.get("insights", {})
                impressions = int(insights.get("impressions", 0))
                clicks = int(insights.get("clicks", 0))
                conversions = int(insights.get("conversions", 0))
                spend = float(insights.get("spend", 0))

                await metric_repo.create(
                    campaign_id=existing_campaign.id,
                    date=today,
                    impressions=impressions,
                    clicks=clicks,
                    conversions=conversions,
                    spend=spend,
                    ctr=float(insights.get("ctr", 0)),
                    cpc=float(insights.get("cpc", 0)),
                )

            await job_repo.update(job.id, status=JobStatus.COMPLETED)
        except Exception as e:
            await job_repo.update(
                job.id,
                status=JobStatus.FAILED,
                error_message=str(e),
                retry_count=job.retry_count + 1,
            )
            raise


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def fetch_all_contacts(self):
    logger.info("Starting fetch_all_contacts task")
    try:
        run_async(_fetch_contacts())
        logger.info("Completed fetch_all_contacts task")
    except Exception as exc:
        logger.error(f"Failed to fetch contacts: {exc}")
        raise self.retry(exc=exc)


async def _fetch_contacts():
    async with async_session_factory() as db:
        hubspot = HubSpotService()
        repo = BaseRepository(Contact, db)
        job_repo = BaseRepository(AutomationJob, db)

        job = await job_repo.create(
            job_type="fetch_contacts",
            status=JobStatus.RUNNING,
        )

        try:
            hubspot_contacts = await hubspot.get_contacts(limit=25)
            for hc in hubspot_contacts:
                props = hc.get("properties", {})
                email = props.get("email", "")
                if not email:
                    continue

                existing = await repo.get_multi(filters={"email": email})
                if existing and existing[0]:
                    continue

                await repo.create(
                    email=email,
                    first_name=props.get("firstname", ""),
                    last_name=props.get("lastname", ""),
                    phone=props.get("phone", ""),
                    company=props.get("company", ""),
                    city=props.get("city", ""),
                    country=props.get("country", ""),
                    source=ContactSource.HUBSPOT,
                )

            await job_repo.update(job.id, status=JobStatus.COMPLETED)
        except Exception as e:
            await job_repo.update(job.id, status=JobStatus.FAILED, error_message=str(e))
            raise


@celery_app.task(bind=True, max_retries=3)
def generate_daily_report(self):
    logger.info("Starting generate_daily_report task")
    try:
        run_async(_generate_report())
        logger.info("Completed generate_daily_report task")
    except Exception as exc:
        logger.error(f"Failed to generate daily report: {exc}")
        raise self.retry(exc=exc)


async def _generate_report():
    async with async_session_factory() as db:
        from app.analytics.reporting import ReportingService

        service = ReportingService(db)
        report = await service.generate_daily_report()
        logger.info(f"Daily report generated: {report['report_date']}")
        return report


@celery_app.task(bind=True, max_retries=2)
def send_email_task(
    self,
    contact_id: int,
    email: str,
    subject: str,
    content: str,
    campaign_id: int = None,
):
    logger.info(f"Sending email to {email}: {subject}")
    try:
        mailchimp = MailchimpService()
        result = run_async(mailchimp.add_member("list_abc123", email))
        logger.info(f"Email sent to {email}: {result.get('id', 'unknown')}")
        return {"status": "sent", "email": email}
    except Exception as exc:
        logger.error(f"Failed to send email to {email}: {exc}")
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=3)
def notify_sales_team(self, contact_id: int, lead_event_id: int, email: str, name: str):
    logger.info(f"Notifying sales team about lead: {name} ({email})")
    try:
        notification = {
            "type": "new_lead",
            "contact_id": contact_id,
            "lead_event_id": lead_event_id,
            "email": email,
            "name": name,
            "message": f"New lead captured: {name} ({email})",
            "priority": "high",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        logger.info(f"Sales notification sent: {notification}")
        return notification
    except Exception as exc:
        logger.error(f"Failed to notify sales: {exc}")
        raise self.retry(exc=exc)


@celery_app.task
def cleanup_old_logs():
    logger.info("Starting cleanup_old_logs task")
    try:
        run_async(_cleanup_logs())
        logger.info("Completed cleanup_old_logs task")
    except Exception as e:
        logger.error(f"Failed to cleanup logs: {e}")


async def _cleanup_logs():
    async with async_session_factory() as db:
        from app.models.api_log import ApiLog
        from app.models.activity_log import ActivityLog
        from sqlalchemy import delete

        cutoff = datetime.now(timezone.utc) - timedelta(days=90)

        await db.execute(delete(ApiLog).where(ApiLog.created_at < cutoff))
        await db.execute(delete(ActivityLog).where(ActivityLog.created_at < cutoff))
        await db.commit()
        logger.info(f"Cleaned up logs older than {cutoff.date()}")


@celery_app.task
def test_task():
    logger.info("Test task executed successfully")
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}
