from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta, timezone
from app.repositories.base import BaseRepository
from app.models.automation_job import AutomationJob, JobStatus


class AutomationJobRepository(BaseRepository[AutomationJob]):
    def __init__(self, db: AsyncSession):
        super().__init__(AutomationJob, db)

    async def get_recent_failures(self, hours: int = 24) -> list:
        since = datetime.now(timezone.utc) - timedelta(hours=hours)
        query = (
            select(AutomationJob)
            .where(
                AutomationJob.status == JobStatus.FAILED,
                AutomationJob.created_at >= since,
            )
            .order_by(AutomationJob.created_at.desc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_stats(self) -> dict:
        total = await self.count()
        completed = await self.count({"status": JobStatus.COMPLETED})
        failed = await self.count({"status": JobStatus.FAILED})
        running = await self.count({"status": JobStatus.RUNNING})
        pending = await self.count({"status": JobStatus.PENDING})
        return {
            "total": total,
            "completed": completed,
            "failed": failed,
            "running": running,
            "pending": pending,
        }
