import random
import asyncio
from datetime import datetime, timedelta
from typing import Optional
from app.core.config import get_settings

settings = get_settings()


class GoogleAnalyticsService:
    def __init__(self):
        self.base_url = "https://analyticsdata.googleapis.com/v1beta"
        self.mock_seed = settings.MOCK_DATA_SEED
        random.seed(self.mock_seed)

    async def _simulate_delay(self):
        delay = random.uniform(
            settings.SIMULATED_API_DELAY_MIN,
            settings.SIMULATED_API_DELAY_MAX,
        )
        await asyncio.sleep(delay)

    async def get_realtime_data(self, property_id: str = "123456789") -> dict:
        await self._simulate_delay()
        active_users = random.randint(10, 500)
        return {
            "property_id": property_id,
            "kind": "analyticsData#realtimeReport",
            "rows": [
                {
                    "dimension_values": ["All Users"],
                    "metric_values": [str(active_users)],
                }
            ],
            "totals": [
                {
                    "metric_values": [
                        str(active_users),
                        str(random.randint(50, 2000)),
                        str(random.randint(20, 500)),
                    ]
                }
            ],
            "maximums": [{"metric_values": ["500", "5000", "1000"]}],
            "minimums": [{"metric_values": ["0", "0", "0"]}],
        }

    async def get_analytics_data(
        self,
        property_id: str = "123456789",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> dict:
        await self._simulate_delay()
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")

        total_users = random.randint(1000, 50000)
        total_sessions = random.randint(int(total_users * 1.2), int(total_users * 3))
        total_pageviews = random.randint(
            int(total_sessions * 2), int(total_sessions * 5)
        )

        return {
            "property_id": property_id,
            "date_range": {"start": start_date, "end": end_date},
            "totals": [
                {
                    "metric_values": [
                        str(total_users),
                        str(total_sessions),
                        str(total_pageviews),
                        str(
                            round(total_sessions / total_users, 2)
                            if total_users > 0
                            else 0
                        ),
                        str(
                            round(total_pageviews / total_sessions, 2)
                            if total_sessions > 0
                            else 0
                        ),
                        str(round(random.uniform(1, 10), 2)),
                        str(round(random.uniform(30, 300), 2)),
                    ]
                }
            ],
            "metrics": [
                {"name": "totalUsers"},
                {"name": "sessions"},
                {"name": "screenPageViews"},
                {"name": "sessionsPerUser"},
                {"name": "screenPageViewsPerSession"},
                {"name": "conversionRate"},
                {"name": "averageSessionDuration"},
            ],
        }

    async def get_acquisition_channels(
        self, property_id: str = "123456789"
    ) -> list[dict]:
        await self._simulate_delay()
        channels = [
            "Organic Search",
            "Paid Search",
            "Social",
            "Direct",
            "Referral",
            "Email",
            "Display",
        ]
        data = []
        for channel in channels:
            users = random.randint(100, 10000)
            sessions = random.randint(int(users * 1.1), int(users * 2.5))
            data.append(
                {
                    "channel": channel,
                    "users": users,
                    "sessions": sessions,
                    "engagement_rate": round(random.uniform(0.3, 0.8), 2),
                    "conversion_rate": round(random.uniform(0.01, 0.1), 4),
                }
            )
        return sorted(data, key=lambda x: x["users"], reverse=True)

    async def get_events(self, property_id: str = "123456789") -> list[dict]:
        await self._simulate_delay()
        event_names = [
            "page_view",
            "session_start",
            "click",
            "form_submit",
            "purchase",
            "sign_up",
            "login",
            "search",
            "download",
        ]
        return [
            {
                "event_name": name,
                "count": random.randint(100, 50000),
                "unique_users": random.randint(50, 10000),
                "conversion_rate": round(random.uniform(0.01, 0.15), 4),
            }
            for name in event_names
        ]
