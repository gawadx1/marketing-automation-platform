from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import date
from app.api.deps import get_db, get_campaign_repo, get_reporting_service, get_metrics_service
from app.schemas.dashboard import DashboardResponse, DailyReport
from app.core.cache import cache_get, cache_set

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("", response_model=DashboardResponse)
async def get_dashboard(db: AsyncSession = Depends(get_db)):
    cached = await cache_get("dashboard:overview")
    if cached:
        return DashboardResponse(**cached)

    metrics_service = await get_metrics_service(db)
    campaign_repo = await get_campaign_repo(db)

    overview = await metrics_service.get_dashboard_overview()
    top_campaigns = await campaign_repo.get_top_campaigns(limit=5)
    daily_stats = await campaign_repo.get_daily_stats(days=30)
    weekly_growth = await metrics_service.get_growth_rate(days=7)
    monthly_growth = await metrics_service.get_growth_rate(days=30)

    from datetime import datetime

    response = DashboardResponse(
        overview=overview,
        top_campaigns=top_campaigns,
        daily_stats=daily_stats,
        weekly_growth=weekly_growth,
        monthly_growth=monthly_growth,
        last_updated=datetime.now(),
    )
    await cache_set("dashboard:overview", response.model_dump(), ttl=120)
    return response


@router.get("/metrics", response_model=dict)
async def get_metrics(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
):
    from datetime import date as d, timedelta

    if not end_date:
        end_date = d.today()
    if not start_date:
        start_date = end_date - timedelta(days=30)

    repo = await get_campaign_repo(db)
    metrics = await repo.get_aggregated_metrics(start_date, end_date)
    daily_stats = await repo.get_daily_stats(days=(end_date - start_date).days or 1)
    return {**metrics, "daily_stats": daily_stats}


@router.get("/report", response_model=DailyReport)
async def get_daily_report(report_date: Optional[date] = None, db: AsyncSession = Depends(get_db)):
    service = await get_reporting_service(db)
    report = await service.generate_daily_report(report_date)
    return report


@router.get("/report/csv")
async def get_csv_report(report_date: Optional[date] = None, db: AsyncSession = Depends(get_db)):
    service = await get_reporting_service(db)
    csv_content = await service.generate_csv_report(report_date)
    filename = f"report_{report_date or date.today()}.csv"
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
