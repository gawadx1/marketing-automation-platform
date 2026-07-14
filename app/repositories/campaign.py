from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import date, timedelta, datetime
from app.repositories.base import BaseRepository
from app.models.campaign import Campaign
from app.models.campaign_metric import CampaignMetric


class CampaignRepository(BaseRepository[Campaign]):
    def __init__(self, db: AsyncSession):
        super().__init__(Campaign, db)

    async def get_with_metrics(self, campaign_id: int) -> tuple:
        campaign = await self.get(campaign_id)
        if not campaign:
            return None, []
        result = await self.db.execute(
            select(CampaignMetric)
            .where(CampaignMetric.campaign_id == campaign_id)
            .order_by(CampaignMetric.date.desc())
        )
        metrics = list(result.scalars().all())
        return campaign, metrics

    async def get_aggregated_metrics(
        self, start_date: date = None, end_date: date = None
    ) -> dict:
        query = select(
            func.coalesce(func.sum(CampaignMetric.spend), 0).label("total_spend"),
            func.coalesce(func.sum(CampaignMetric.clicks), 0).label("total_clicks"),
            func.coalesce(func.sum(CampaignMetric.impressions), 0).label(
                "total_impressions"
            ),
            func.coalesce(func.sum(CampaignMetric.conversions), 0).label(
                "total_conversions"
            ),
            func.coalesce(func.sum(CampaignMetric.leads), 0).label("total_leads"),
        ).select_from(CampaignMetric)

        if start_date:
            query = query.where(CampaignMetric.date >= start_date)
        if end_date:
            query = query.where(CampaignMetric.date <= end_date)

        result = await self.db.execute(query)
        row = result.one()
        return {
            "total_spend": float(row.total_spend),
            "total_clicks": int(row.total_clicks),
            "total_impressions": int(row.total_impressions),
            "total_conversions": int(row.total_conversions),
            "total_leads": int(row.total_leads),
        }

    async def get_daily_stats(self, days: int = 30) -> list:
        start = date.today() - timedelta(days=days)
        query = (
            select(
                CampaignMetric.date,
                func.sum(CampaignMetric.spend).label("spend"),
                func.sum(CampaignMetric.clicks).label("clicks"),
                func.sum(CampaignMetric.impressions).label("impressions"),
                func.sum(CampaignMetric.conversions).label("conversions"),
                func.sum(CampaignMetric.leads).label("leads"),
            )
            .where(CampaignMetric.date >= start)
            .group_by(CampaignMetric.date)
            .order_by(CampaignMetric.date)
        )
        result = await self.db.execute(query)
        rows = result.all()
        return [
            {
                "date": row.date,
                "spend": float(row.spend),
                "clicks": int(row.clicks),
                "impressions": int(row.impressions),
                "conversions": int(row.conversions),
                "leads": int(row.leads),
            }
            for row in rows
        ]

    async def get_top_campaigns(self, limit: int = 5) -> list:
        today = date.today()
        thirty_days_ago = today - timedelta(days=30)
        query = (
            select(
                Campaign.id,
                Campaign.name,
                Campaign.platform,
                Campaign.status,
                Campaign.spent,
                func.coalesce(func.sum(CampaignMetric.impressions), 0).label(
                    "impressions"
                ),
                func.coalesce(func.sum(CampaignMetric.clicks), 0).label("clicks"),
                func.coalesce(func.sum(CampaignMetric.conversions), 0).label(
                    "conversions"
                ),
            )
            .join(
                CampaignMetric, CampaignMetric.campaign_id == Campaign.id, isouter=True
            )
            .where(
                and_(
                    CampaignMetric.date >= thirty_days_ago,
                    CampaignMetric.date <= today,
                )
            )
            .group_by(Campaign.id)
            .order_by(func.coalesce(func.sum(CampaignMetric.clicks), 0).desc())
            .limit(limit)
        )
        result = await self.db.execute(query)
        rows = result.all()
        campaigns = []
        for row in rows:
            impressions = int(row.impressions)
            clicks = int(row.clicks)
            conversions = int(row.conversions)
            campaigns.append(
                {
                    "id": row.id,
                    "name": row.name,
                    "platform": row.platform.value
                    if hasattr(row.platform, "value")
                    else row.platform,
                    "status": row.status.value
                    if hasattr(row.status, "value")
                    else row.status,
                    "spend": float(row.spent),
                    "impressions": impressions,
                    "clicks": clicks,
                    "conversions": conversions,
                    "ctr": round(
                        (clicks / impressions * 100) if impressions > 0 else 0, 2
                    ),
                    "cpc": round(float(row.spent) / clicks if clicks > 0 else 0, 2),
                    "cpa": round(
                        float(row.spent) / conversions if conversions > 0 else 0, 2
                    ),
                }
            )
        return campaigns
