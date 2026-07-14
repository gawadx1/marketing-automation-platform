import csv
import io
from datetime import date, datetime, timedelta, timezone
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from app.repositories.campaign import CampaignRepository
from app.models.campaign import Campaign
from app.models.campaign_metric import CampaignMetric


class ReportingService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.campaign_repo = CampaignRepository(db)

    async def generate_daily_report(self, report_date: Optional[date] = None) -> dict:
        if report_date is None:
            report_date = date.today() - timedelta(days=1)

        metrics = await self.campaign_repo.get_aggregated_metrics(
            start_date=report_date, end_date=report_date
        )

        total_spend = metrics["total_spend"]
        total_clicks = metrics["total_clicks"]
        total_impressions = metrics["total_impressions"]
        total_conversions = metrics["total_conversions"]

        ctr = round(
            (total_clicks / total_impressions * 100) if total_impressions > 0 else 0, 2
        )
        cpc = round(total_spend / total_clicks, 2) if total_clicks > 0 else 0
        cpa = round(total_spend / total_conversions, 2) if total_conversions > 0 else 0

        top_campaign = await self._get_top_campaign(report_date)
        worst_campaign = await self._get_worst_campaign(report_date)

        return {
            "report_date": report_date,
            "total_spend": total_spend,
            "total_clicks": total_clicks,
            "total_impressions": total_impressions,
            "total_conversions": total_conversions,
            "total_leads": metrics["total_leads"],
            "ctr": ctr,
            "cpc": cpc,
            "cpa": cpa,
            "top_campaign": top_campaign,
            "worst_campaign": worst_campaign,
            "generated_at": datetime.now(timezone.utc),
        }

    async def _get_top_campaign(self, report_date: date) -> Optional[str]:
        query = (
            select(Campaign.name, func.sum(CampaignMetric.clicks).label("total_clicks"))
            .join(CampaignMetric, CampaignMetric.campaign_id == Campaign.id)
            .where(CampaignMetric.date == report_date)
            .group_by(Campaign.name)
            .order_by(func.sum(CampaignMetric.clicks).desc())
            .limit(1)
        )
        result = await self.db.execute(query)
        row = result.first()
        return row.name if row else None

    async def _get_worst_campaign(self, report_date: date) -> Optional[str]:
        query = (
            select(Campaign.name, func.sum(CampaignMetric.clicks).label("total_clicks"))
            .join(CampaignMetric, CampaignMetric.campaign_id == Campaign.id)
            .where(CampaignMetric.date == report_date)
            .group_by(Campaign.name)
            .order_by(func.sum(CampaignMetric.clicks).asc())
            .limit(1)
        )
        result = await self.db.execute(query)
        row = result.first()
        return row.name if row else None

    async def generate_csv_report(self, report_date: Optional[date] = None) -> str:
        if report_date is None:
            report_date = date.today() - timedelta(days=1)

        query = (
            select(
                Campaign.name,
                Campaign.platform,
                CampaignMetric.date,
                CampaignMetric.impressions,
                CampaignMetric.clicks,
                CampaignMetric.conversions,
                CampaignMetric.spend,
                CampaignMetric.leads,
                CampaignMetric.ctr,
                CampaignMetric.cpc,
                CampaignMetric.cpa,
            )
            .join(CampaignMetric, CampaignMetric.campaign_id == Campaign.id)
            .where(CampaignMetric.date == report_date)
            .order_by(Campaign.name)
        )
        result = await self.db.execute(query)
        rows = result.all()

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(
            [
                "Campaign",
                "Platform",
                "Date",
                "Impressions",
                "Clicks",
                "Conversions",
                "Spend",
                "Leads",
                "CTR",
                "CPC",
                "CPA",
            ]
        )
        for row in rows:
            writer.writerow(
                [
                    row.name,
                    row.platform.value
                    if hasattr(row.platform, "value")
                    else row.platform,
                    row.date,
                    row.impressions,
                    row.clicks,
                    row.conversions,
                    row.spend,
                    row.leads,
                    row.ctr,
                    row.cpc,
                    row.cpa,
                ]
            )

        return output.getvalue()
