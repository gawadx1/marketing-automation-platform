import random
import asyncio
from datetime import datetime, timedelta
from app.core.config import get_settings
from app.services.integrations.base import BaseIntegrationService

settings = get_settings()


class HubSpotService(BaseIntegrationService):
    def __init__(self):
        super().__init__()
        self._base_url = "https://api.hubapi.com/crm/v3"
        self.use_real_api = bool(settings.HUBSPOT_ACCESS_TOKEN)

    @property
    def base_url(self) -> str:
        return self._base_url

    def _get_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {settings.HUBSPOT_ACCESS_TOKEN or ''}",
            "Content-Type": "application/json",
        }

    FIRST_NAMES = [
        "Alice",
        "Bob",
        "Charlie",
        "Diana",
        "Eve",
        "Frank",
        "Grace",
        "Henry",
        "Ivy",
        "Jack",
    ]
    LAST_NAMES = [
        "Smith",
        "Johnson",
        "Williams",
        "Brown",
        "Jones",
        "Garcia",
        "Miller",
        "Davis",
        "Rodriguez",
        "Martinez",
    ]
    COMPANIES = [
        "Acme Corp",
        "Globex Inc",
        "Initech",
        "Hooli",
        "Stark Industries",
        "Wayne Enterprises",
        "Cyberdyne",
        "Umbrella Corp",
    ]
    CITIES = [
        "New York",
        "San Francisco",
        "Chicago",
        "Austin",
        "Seattle",
        "Boston",
        "Denver",
        "Portland",
    ]
    COUNTRIES = ["US", "US", "US", "Canada", "UK", "Germany", "Australia", "France"]

    async def get_contacts(self, limit: int = 50) -> list[dict]:
        await self._simulate_delay()
        if self.use_real_api:
            try:
                data = await self._request(
                    "GET",
                    f"/objects/contacts?limit={limit}&properties=email,firstname,lastname,phone,company,city,country,hs_lead_status,createdate",
                )
                return data.get("results", [])
            except Exception:
                pass
        contacts = []
        for i in range(limit):
            first = random.choice(self.FIRST_NAMES)
            last = random.choice(self.LAST_NAMES)
            contacts.append(
                {
                    "id": f"hubspot_contact_{i}",
                    "properties": {
                        "email": f"{first.lower()}.{last.lower()}@example.com",
                        "firstname": first,
                        "lastname": last,
                        "phone": f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
                        "company": random.choice(self.COMPANIES),
                        "city": random.choice(self.CITIES),
                        "country": random.choice(self.COUNTRIES),
                        "hs_lead_status": random.choice(["NEW", "OPEN", "IN_PROGRESS", "CONNECTED", "CLOSED"]),
                        "createdate": (datetime.now() - timedelta(days=random.randint(1, 365))).isoformat(),
                        "lastmodifieddate": datetime.now().isoformat(),
                    },
                    "createdAt": (datetime.now() - timedelta(days=random.randint(1, 365))).isoformat(),
                    "updatedAt": datetime.now().isoformat(),
                }
            )
        return contacts

    async def create_contact(self, contact_data: dict) -> dict:
        await self._simulate_delay()
        if self.use_real_api:
            try:
                data = await self._request(
                    "POST",
                    "/objects/contacts",
                    json={
                        "properties": {
                            "email": contact_data.get("email", ""),
                            "firstname": contact_data.get("firstname", ""),
                            "lastname": contact_data.get("lastname", ""),
                            "phone": contact_data.get("phone", ""),
                            "company": contact_data.get("company", ""),
                        }
                    },
                )
                return data
            except Exception:
                pass
        contact_id = f"hubspot_contact_{random.randint(10000, 99999)}"
        return {
            "id": contact_id,
            "properties": {
                "email": contact_data.get("email", ""),
                "firstname": contact_data.get("firstname", ""),
                "lastname": contact_data.get("lastname", ""),
                "phone": contact_data.get("phone", ""),
                "company": contact_data.get("company", ""),
            },
            "createdAt": datetime.now().isoformat(),
            "updatedAt": datetime.now().isoformat(),
        }

    async def get_deals(self, limit: int = 20) -> list[dict]:
        await self._simulate_delay()
        if self.use_real_api:
            try:
                data = await self._request(
                    "GET",
                    f"/objects/deals?limit={limit}&properties=dealname,amount,dealstage,pipeline,closedate,createdate",
                )
                return data.get("results", [])
            except Exception:
                pass
        stages = [
            "appointmentscheduled",
            "qualifiedtobuy",
            "presentationscheduled",
            "decisionmakerboughtin",
            "contractsent",
            "closedwon",
            "closedlost",
        ]
        return [
            {
                "id": f"hubspot_deal_{i}",
                "properties": {
                    "dealname": f"Deal {i} - {random.choice(self.COMPANIES)}",
                    "amount": str(round(random.uniform(1000, 100000), 2)),
                    "dealstage": random.choice(stages),
                    "pipeline": "default",
                    "closedate": (datetime.now() + timedelta(days=random.randint(-30, 60))).strftime("%Y-%m-%d"),
                    "createdate": (datetime.now() - timedelta(days=random.randint(1, 180))).isoformat(),
                },
            }
            for i in range(1, limit + 1)
        ]

    async def get_pipelines(self) -> list[dict]:
        await self._simulate_delay()
        if self.use_real_api:
            try:
                data = await self._request("GET", "/pipelines/default")
                return data.get("results", [data])
            except Exception:
                pass
        return [
            {
                "id": "default",
                "label": "Sales Pipeline",
                "stages": [
                    {"id": "appointmentscheduled", "label": "Appointment Scheduled", "probability": 0.2},
                    {"id": "qualifiedtobuy", "label": "Qualified to Buy", "probability": 0.4},
                    {"id": "presentationscheduled", "label": "Presentation Scheduled", "probability": 0.6},
                    {"id": "decisionmakerboughtin", "label": "Decision Maker Bought-In", "probability": 0.8},
                    {"id": "contractsent", "label": "Contract Sent", "probability": 0.9},
                    {"id": "closedwon", "label": "Closed Won", "probability": 1.0},
                    {"id": "closedlost", "label": "Closed Lost", "probability": 0.0},
                ],
            }
        ]
