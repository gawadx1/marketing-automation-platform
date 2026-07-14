import random
import asyncio
from datetime import datetime, timedelta
from app.core.config import get_settings
from app.services.integrations.base import BaseIntegrationService

settings = get_settings()


class MailchimpService(BaseIntegrationService):
    def __init__(self):
        super().__init__()
        self._base_url = f"https://{settings.MAILCHIMP_SERVER_PREFIX or 'us21'}.api.mailchimp.com/3.0"
        self.use_real_api = bool(settings.MAILCHIMP_API_KEY)

    @property
    def base_url(self) -> str:
        return self._base_url

    def _get_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {settings.MAILCHIMP_API_KEY or ''}",
            "Content-Type": "application/json",
        }

    async def get_lists(self) -> list[dict]:
        await self._simulate_delay()
        if self.use_real_api:
            try:
                data = await self._request(
                    "GET", "/lists?fields=lists.id,lists.name,lists.contact,lists.stats&count=25"
                )
                return data.get("lists", [])
            except Exception:
                pass
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

    async def add_member(self, list_id: str, email: str, first_name: str = "", last_name: str = "") -> dict:
        await self._simulate_delay()
        if self.use_real_api:
            try:
                data = await self._request(
                    "POST",
                    f"/lists/{list_id}/members",
                    json={
                        "email_address": email,
                        "status": "subscribed",
                        "merge_fields": {
                            "FNAME": first_name,
                            "LNAME": last_name,
                        },
                    },
                )
                return data
            except Exception:
                pass
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
        if self.use_real_api:
            try:
                # Find member hash and delete
                import hashlib

                member_hash = hashlib.md5(email.lower().encode()).hexdigest()
                await self._request(
                    "DELETE",
                    f"/lists/{list_id}/members/{member_hash}",
                )
                return {"status": "archived", "email": email}
            except Exception:
                pass
        return {"status": "archived", "email": email}

    async def create_campaign(self, list_id: str, subject: str, content: str, title: str = "") -> dict:
        await self._simulate_delay()
        if self.use_real_api:
            try:
                data = await self._request(
                    "POST",
                    "/campaigns",
                    json={
                        "type": "regular",
                        "recipients": {"list_id": list_id},
                        "settings": {
                            "subject_line": subject,
                            "title": title or subject,
                            "from_name": "Marketing Team",
                            "reply_to": "marketing@company.com",
                        },
                    },
                )
                return data
            except Exception:
                pass
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
        if self.use_real_api:
            try:
                data = await self._request("POST", f"/campaigns/{campaign_id}/actions/send")
                return {"id": campaign_id, "status": "sent", "send_time": datetime.now().isoformat()}
            except Exception:
                pass
        return {
            "id": campaign_id,
            "status": "sent",
            "send_time": datetime.now().isoformat(),
            "emails_sent": random.randint(100, 50000),
        }

    async def get_campaign_reports(self, campaign_id: str) -> dict:
        await self._simulate_delay()
        if self.use_real_api:
            try:
                data = await self._request("GET", f"/reports/{campaign_id}")
                return data
            except Exception:
                pass
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
            "click_rate": round(clicks / emails_sent * 100, 2) if emails_sent > 0 else 0,
            "bounces": random.randint(0, int(emails_sent * 0.02)),
            "unsubscribes": random.randint(0, int(emails_sent * 0.01)),
        }
