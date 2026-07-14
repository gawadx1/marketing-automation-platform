"""Tests for simulated integration services."""

import pytest
from app.services.integrations.google_ads import GoogleAdsService
from app.services.integrations.meta_ads import MetaAdsService
from app.services.integrations.hubspot import HubSpotService
from app.services.integrations.mailchimp import MailchimpService
from app.services.integrations.google_analytics import GoogleAnalyticsService


class TestGoogleAdsService:
    @pytest.mark.asyncio
    async def test_get_campaigns(self):
        service = GoogleAdsService()
        campaigns = await service.get_campaigns()
        assert len(campaigns) > 0
        assert "id" in campaigns[0]
        assert "name" in campaigns[0]
        assert "status" in campaigns[0]

    @pytest.mark.asyncio
    async def test_get_campaign_stats(self):
        service = GoogleAdsService()
        stats = await service.get_campaign_stats("google_campaign_1")
        assert "impressions" in stats
        assert "clicks" in stats
        assert "cost" in stats
        assert stats["impressions"] > 0

    @pytest.mark.asyncio
    async def test_create_campaign(self):
        service = GoogleAdsService()
        result = await service.create_campaign({"name": "Test", "budget": 1000})
        assert "id" in result
        assert result["status"] == "enabled"


class TestMetaAdsService:
    @pytest.mark.asyncio
    async def test_get_campaigns(self):
        service = MetaAdsService()
        campaigns = await service.get_campaigns()
        assert len(campaigns) > 0
        assert "objective" in campaigns[0]

    @pytest.mark.asyncio
    async def test_get_lead_forms(self):
        service = MetaAdsService()
        forms = await service.get_lead_forms()
        assert len(forms) > 0
        assert "questions" in forms[0]


class TestHubSpotService:
    @pytest.mark.asyncio
    async def test_get_contacts(self):
        service = HubSpotService()
        contacts = await service.get_contacts(limit=5)
        assert len(contacts) == 5
        assert "properties" in contacts[0]
        assert "email" in contacts[0]["properties"]

    @pytest.mark.asyncio
    async def test_create_contact(self):
        service = HubSpotService()
        result = await service.create_contact(
            {
                "email": "new@example.com",
                "firstname": "Jane",
                "lastname": "Doe",
            }
        )
        assert result["properties"]["email"] == "new@example.com"

    @pytest.mark.asyncio
    async def test_get_deals(self):
        service = HubSpotService()
        deals = await service.get_deals(limit=3)
        assert len(deals) <= 3
        assert "properties" in deals[0]


class TestMailchimpService:
    @pytest.mark.asyncio
    async def test_add_member(self):
        service = MailchimpService()
        result = await service.add_member("list_abc123", "test@example.com", "Test", "User")
        assert result["status"] == "subscribed"
        assert result["email_address"] == "test@example.com"

    @pytest.mark.asyncio
    async def test_create_campaign(self):
        service = MailchimpService()
        result = await service.create_campaign(
            list_id="list_abc123",
            subject="Test Subject",
            content="<h1>Hello</h1>",
            title="Test Campaign",
        )
        assert "id" in result
        assert result["settings"]["subject_line"] == "Test Subject"

    @pytest.mark.asyncio
    async def test_get_campaign_reports(self):
        service = MailchimpService()
        result = await service.get_campaign_reports("campaign_123")
        assert "emails_sent" in result
        assert "open_rate" in result


class TestGoogleAnalyticsService:
    @pytest.mark.asyncio
    async def test_realtime_data(self):
        service = GoogleAnalyticsService()
        data = await service.get_realtime_data()
        assert "rows" in data

    @pytest.mark.asyncio
    async def test_analytics_data(self):
        service = GoogleAnalyticsService()
        data = await service.get_analytics_data()
        assert "totals" in data

    @pytest.mark.asyncio
    async def test_acquisition_channels(self):
        service = GoogleAnalyticsService()
        channels = await service.get_acquisition_channels()
        assert len(channels) > 0
        assert "channel" in channels[0]
