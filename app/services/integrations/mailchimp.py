import random
import asyncio
from datetime import datetime, timedelta
from app.core.config import get_settings

settings = get_settings()


class MailchimpService:
    def __init__(self):
        self.base_url = "https://us21.api.mailchimp.com/3.0"
        self.mock_seed = settings.MOCK_DATA_SEED
        random.seed(self.mock_seed)

    async def _simulate_delay(self):
        delay = random.uniform(
            settings.SIMULATED_API_DELAY_MIN,
            settings.SIMULATED_API_DELAY_MAX,
        )
        await asyncio.sleep(delay)

    async def get_lists(self) -> list[dict]:
        await self._simulate_delay()
        return [
            {
                "id": "list_abc123",
                "name": "Main Newsletter",
                "contact": {
                    "company": "MarketingCo",
                    "address1": "123 Main St",
                    "city": "San Francisco",
                    "country": "US",
                },
                "stats": {
                    "member_count": random.randint(1000, 50000),
                    "open_rate": round(random.uniform(15, 35), 2),
                    "click_rate": round(random.uniform(2, 8), 2),
                },
            },
            {
                "id": "list_def456",
                "name": "Prospects",
                "contact": {
                    "company": "MarketingCo",
                    "address1": "123 Main St",
                    "city": "San Francisco",
                    "country": "US",
                },
                "stats": {
                    "member_count": random.randint(500, 10000),
                    "open_rate": round(random.uniform(20, 40), 2),
                    "click_rate": round(random.uniform(3, 10), 2),
                },
            },
        ]

    async def add_member(
        self, list_id: str, email: str, first_name: str = "", last_name: str = ""
    ) -> dict:
        await self._simulate_delay()
        return {
            "id": f"member_{random.randint(100000, 999999)}",
            "email_address": email,
            "unique_email_id": f"uuid_{random.randint(10000, 99999)}",
            "contact_id": random.randint(1000, 9999),
            "full_name": f"{first_name} {last_name}",
            "status": "subscribed",
            "list_id": list_id,
            "timestamp_opt": datetime.now().isoformat(),
            "last_changed": datetime.now().isoformat(),
        }

    async def remove_member(self, list_id: str, email: str) -> dict:
        await self._simulate_delay()
        return {"status": "archived", "email": email}

    async def create_campaign(
        self, list_id: str, subject: str, content: str, title: str = ""
    ) -> dict:
        await self._simulate_delay()
        return {
            "id": f"campaign_{random.randint(100000, 999999)}",
            "type": "regular",
            "status": "save",
            "settings": {
                "subject_line": subject,
                "title": title or subject,
                "from_name": "Marketing Team",
                "reply_to": "marketing@company.com",
            },
            "recipients": {"list_id": list_id},
        }

    async def send_campaign(self, campaign_id: str) -> dict:
        await self._simulate_delay()
        return {
            "id": campaign_id,
            "status": "sent",
            "send_time": datetime.now().isoformat(),
            "emails_sent": random.randint(100, 50000),
        }

    async def get_campaign_reports(self, campaign_id: str) -> dict:
        await self._simulate_delay()
        emails_sent = random.randint(1000, 50000)
        opens = random.randint(int(emails_sent * 0.15), int(emails_sent * 0.35))
        clicks = random.randint(int(opens * 0.1), int(opens * 0.3))
        return {
            "id": campaign_id,
            "emails_sent": emails_sent,
            "opens": opens,
            "unique_opens": int(opens * random.uniform(0.6, 0.9)),
            "open_rate": round(opens / emails_sent * 100, 2) if emails_sent > 0 else 0,
            "clicks": clicks,
            "unique_clicks": int(clicks * random.uniform(0.7, 0.9)),
            "click_rate": round(clicks / emails_sent * 100, 2)
            if emails_sent > 0
            else 0,
            "bounces": random.randint(0, int(emails_sent * 0.02)),
            "unsubscribes": random.randint(0, int(emails_sent * 0.01)),
        }
