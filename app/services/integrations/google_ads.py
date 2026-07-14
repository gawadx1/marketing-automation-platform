import random
import asyncio
from datetime import datetime, timedelta
from typing import Optional
from app.core.config import get_settings

settings = get_settings()


class GoogleAdsService:
    def __init__(self):
        self.base_url = "https://googleads.googleapis.com/v15"

    async def _simulate_delay(self):
        delay = random.uniform(
            settings.SIMULATED_API_DELAY_MIN,
            settings.SIMULATED_API_DELAY_MAX,
        )
        await asyncio.sleep(delay)

    async def get_campaigns(self, customer_id: str = "123-456-7890") -> list[dict]:
        await self._simulate_delay()
        platforms = ["search", "display", "shopping", "video", "app"]
        statuses = ["enabled", "paused", "removed"]
        return [
            {
                "id": f"google_campaign_{i}",
                "name": f"Google {p.capitalize()} Campaign {i}",
                "status": random.choice(statuses),
                "type": p,
                "budget": round(random.uniform(500, 50000), 2),
                "start_date": (datetime.now() - timedelta(days=random.randint(1, 90))).strftime("%Y-%m-%d"),
                "end_date": (datetime.now() + timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d")
                if random.random() > 0.3
                else None,
                "customer_id": customer_id,
            }
            for i, p in enumerate(platforms, 1)
        ]

    async def get_campaign_stats(self, campaign_id: str, start_date: str = None, end_date: str = None) -> dict:
        await self._simulate_delay()
        impressions = random.randint(1000, 100000)
        clicks = random.randint(int(impressions * 0.01), int(impressions * 0.1))
        conversions = random.randint(int(clicks * 0.05), int(clicks * 0.2))
        cost = round(random.uniform(100, 10000), 2)
        return {
            "campaign_id": campaign_id,
            "impressions": impressions,
            "clicks": clicks,
            "conversions": conversions,
            "cost_micros": int(cost * 1_000_000),
            "cost": cost,
            "average_cpc": round(cost / clicks, 2) if clicks > 0 else 0,
            "ctr": round(clicks / impressions * 100, 2) if impressions > 0 else 0,
            "conversion_rate": round(conversions / clicks * 100, 2) if clicks > 0 else 0,
            "average_position": round(random.uniform(1.0, 5.0), 1),
            "quality_score": random.randint(5, 10),
            "date_range": {"start": start_date, "end": end_date},
        }

    async def get_all_campaigns_stats(self) -> list[dict]:
        campaigns = await self.get_campaigns()
        results = []
        for campaign in campaigns:
            stats = await self.get_campaign_stats(campaign["id"])
            results.append({**campaign, **stats})
        return results

    async def create_campaign(self, campaign_data: dict) -> dict:
        await self._simulate_delay()
        campaign_id = f"google_campaign_{random.randint(1000, 9999)}"
        return {
            "id": campaign_id,
            "name": campaign_data.get("name", "New Campaign"),
            "status": "enabled",
            "type": campaign_data.get("type", "search"),
            "budget": campaign_data.get("budget", 1000),
            "resource_name": f"customers/123-456-7890/campaigns/{campaign_id}",
        }
