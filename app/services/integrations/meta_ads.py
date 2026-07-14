import random
import asyncio
from datetime import datetime, timedelta
from app.core.config import get_settings

settings = get_settings()


class MetaAdsService:
    def __init__(self):
        self.base_url = "https://graph.facebook.com/v18.0"
        self.mock_seed = settings.MOCK_DATA_SEED
        random.seed(self.mock_seed)

    async def _simulate_delay(self):
        delay = random.uniform(
            settings.SIMULATED_API_DELAY_MIN,
            settings.SIMULATED_API_DELAY_MAX,
        )
        await asyncio.sleep(delay)

    async def get_campaigns(self, ad_account_id: str = "act_123456789") -> list[dict]:
        await self._simulate_delay()
        objectives = [
            "awareness",
            "traffic",
            "engagement",
            "leads",
            "sales",
            "video_views",
        ]
        statuses = ["ACTIVE", "PAUSED", "ARCHIVED"]
        return [
            {
                "id": f"meta_campaign_{i}",
                "name": f"Meta {obj.capitalize()} Campaign {i}",
                "status": random.choice(statuses),
                "objective": obj,
                "daily_budget": round(random.uniform(10, 500), 2),
                "lifetime_budget": round(random.uniform(500, 50000), 2),
                "start_time": (
                    datetime.now() - timedelta(days=random.randint(1, 60))
                ).isoformat(),
                "updated_time": datetime.now().isoformat(),
                "account_id": ad_account_id,
            }
            for i, obj in enumerate(objectives, 1)
        ]

    async def get_ad_insights(
        self, campaign_id: str, date_preset: str = "last_30d"
    ) -> list[dict]:
        await self._simulate_delay()
        impressions = random.randint(5000, 200000)
        clicks = random.randint(int(impressions * 0.005), int(impressions * 0.05))
        reach = random.randint(int(impressions * 0.3), int(impressions * 0.8))
        return [
            {
                "campaign_id": campaign_id,
                "date_start": (datetime.now() - timedelta(days=30)).strftime(
                    "%Y-%m-%d"
                ),
                "date_stop": datetime.now().strftime("%Y-%m-%d"),
                "impressions": str(impressions),
                "clicks": str(clicks),
                "reach": str(reach),
                "spend": str(round(random.uniform(100, 5000), 2)),
                "cpc": str(round(random.uniform(0.5, 5.0), 2)),
                "cpm": str(round(random.uniform(5, 50), 2)),
                "ctr": str(round(clicks / impressions * 100, 2)),
                "conversions": str(
                    random.randint(int(clicks * 0.02), int(clicks * 0.15))
                ),
                "cost_per_conversion": str(round(random.uniform(10, 100), 2)),
                "frequency": str(round(random.uniform(1.0, 3.5), 2)),
            }
        ]

    async def get_lead_forms(self, page_id: str = "123456789") -> list[dict]:
        await self._simulate_delay()
        return [
            {
                "id": f"lead_form_{i}",
                "name": f"Lead Form {i} - {random.choice(['Newsletter', 'Webinar', 'Quote', 'Download', 'Demo'])}",
                "status": "ACTIVE",
                "locale": "en_US",
                "created_time": (
                    datetime.now() - timedelta(days=random.randint(1, 60))
                ).isoformat(),
                "page_id": page_id,
                "questions": [
                    {"key": "email", "label": "Email"},
                    {"key": "full_name", "label": "Full Name"},
                    {"key": "phone", "label": "Phone Number"},
                ],
            }
            for i in range(1, 4)
        ]

    async def get_all_campaigns_insights(self) -> list[dict]:
        campaigns = await self.get_campaigns()
        results = []
        for campaign in campaigns:
            insights = await self.get_ad_insights(campaign["id"])
            for insight in insights:
                results.append({**campaign, "insights": insight})
        return results
