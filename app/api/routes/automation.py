from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.api.deps import get_db, get_automation_job_repo
from app.schemas.automation import AutomationJobResponse

router = APIRouter(prefix="/automation", tags=["Automation"])


@router.get("/jobs", response_model=dict)
async def list_automation_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status: Optional[str] = None,
    job_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    repo = await get_automation_job_repo(db)
    filters = {}
    if status:
        filters["status"] = status
    if job_type:
        filters["job_type"] = job_type

    jobs, total = await repo.get_multi(
        skip=skip, limit=limit, filters=filters, order_by="created_at", descending=True
    )
    return {
        "items": [AutomationJobResponse.model_validate(j).model_dump() for j in jobs],
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.get("/jobs/stats", response_model=dict)
async def get_automation_stats(db: AsyncSession = Depends(get_db)):
    repo = await get_automation_job_repo(db)
    stats = await repo.get_stats()
    return stats
