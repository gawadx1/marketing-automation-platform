from datetime import date, timedelta, datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from app.models.campaign_metric import CampaignMetric
from app.models.campaign import Campaign
from app.models.contact import Contact
from app.repositories.campaign import CampaignRepository


class MetricsService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.campaign_repo = CampaignRepository(db)

    async def get_dashboard_overview(self) -> dict:
        today = date.today()
        today_metrics = await self.campaign_repo.get_aggregated_metrics(
            start_date=today, end_date=today
        )

        total_campaigns = await self.campaign_repo.count()
        active_campaigns = await self.campaign_repo.count({"status": "active"})

        result = await self.db.execute(select(func.count(Contact.id)))
        total_contacts = result.scalar() or 0

        return {
            "today_spend": today_metrics["total_spend"],
            "today_clicks": today_metrics["total_clicks"],
            "today_impressions": today_metrics["total_impressions"],
            "today_leads": today_metrics["total_leads"],
            "today_conversions": today_metrics["total_conversions"],
            "total_campaigns": total_campaigns,
            "active_campaigns": active_campaigns,
            "total_contacts": total_contacts,
        }

    async def get_growth_rate(self, days: int = 7) -> float:
        today = date.today()
        current_start = today - timedelta(days=days)
        previous_start = current_start - timedelta(days=days)

        current = await self.campaign_repo.get_aggregated_metrics(
            start_date=current_start, end_date=today
        )
        previous = await self.campaign_repo.get_aggregated_metrics(
            start_date=previous_start, end_date=current_start - timedelta(days=1)
        )

        if previous["total_clicks"] > 0:
            growth = (
                (current["total_clicks"] - previous["total_clicks"])
                / previous["total_clicks"]
                * 100
            )
        else:
            growth = 100.0 if current["total_clicks"] > 0 else 0.0

        return round(growth, 2)

    async def get_monthly_stats(self) -> list[dict]:
        today = date.today()
        start = today - timedelta(days=365)

        query = (
            select(
                func.date_trunc("month", CampaignMetric.date).label("month"),
                func.sum(CampaignMetric.spend).label("spend"),
                func.sum(CampaignMetric.clicks).label("clicks"),
                func.sum(CampaignMetric.impressions).label("impressions"),
                func.sum(CampaignMetric.conversions).label("conversions"),
            )
            .where(CampaignMetric.date >= start)
            .group_by(func.date_trunc("month", CampaignMetric.date))
            .order_by(func.date_trunc("month", CampaignMetric.date))
        )
        result = await self.db.execute(query)
        rows = result.all()
        return [
            {
                "month": row.month,
                "spend": float(row.spend),
                "clicks": int(row.clicks),
                "impressions": int(row.impressions),
                "conversions": int(row.conversions),
            }
            for row in rows
        ]
