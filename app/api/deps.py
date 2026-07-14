from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import async_session_factory
from app.repositories.campaign import CampaignRepository
from app.repositories.contact import ContactRepository, LeadEventRepository
from app.repositories.automation_job import AutomationJobRepository
from app.repositories.user import UserRepository
from app.analytics.reporting import ReportingService
from app.analytics.metrics import MetricsService


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_campaign_repo(db: AsyncSession = None) -> CampaignRepository:
    if db is None:
        async with async_session_factory() as session:
            return CampaignRepository(session)
    return CampaignRepository(db)


async def get_contact_repo(db: AsyncSession = None) -> ContactRepository:
    if db is None:
        async with async_session_factory() as session:
            return ContactRepository(session)
    return ContactRepository(db)


async def get_lead_event_repo(db: AsyncSession = None) -> LeadEventRepository:
    if db is None:
        async with async_session_factory() as session:
            return LeadEventRepository(session)
    return LeadEventRepository(db)


async def get_automation_job_repo(db: AsyncSession = None) -> AutomationJobRepository:
    if db is None:
        async with async_session_factory() as session:
            return AutomationJobRepository(session)
    return AutomationJobRepository(db)


async def get_user_repo(db: AsyncSession = None) -> UserRepository:
    if db is None:
        async with async_session_factory() as session:
            return UserRepository(session)
    return UserRepository(db)


async def get_reporting_service(db: AsyncSession = None) -> ReportingService:
    if db is None:
        async with async_session_factory() as session:
            return ReportingService(session)
    return ReportingService(db)


async def get_metrics_service(db: AsyncSession = None) -> MetricsService:
    if db is None:
        async with async_session_factory() as session:
            return MetricsService(session)
    return MetricsService(db)
