"""Integration tests for API endpoints."""

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.fixture
def client():
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


class TestHealthEndpoints:
    @pytest.mark.asyncio
    async def test_health(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "version" in data

    @pytest.mark.asyncio
    async def test_liveness(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.get("/api/v1/health/live")
        assert response.status_code == 200
        assert response.json()["status"] == "alive"

    @pytest.mark.asyncio
    async def test_root(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data


class TestAuthEndpoints:
    @pytest.mark.asyncio
    async def test_register_and_login(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            register_resp = await ac.post(
                "/api/v1/auth/register",
                json={
                    "email": "testuser@example.com",
                    "username": "testuser",
                    "password": "testpass123",
                    "full_name": "Test User",
                },
            )
            assert register_resp.status_code in (201, 400)

            login_resp = await ac.post(
                "/api/v1/auth/login",
                json={"username": "testuser", "password": "testpass123"},
            )
            assert login_resp.status_code in (200, 401)


class TestCampaignEndpoints:
    @pytest.mark.asyncio
    async def test_list_campaigns(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.get("/api/v1/campaigns")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "skip" in data
        assert "limit" in data

    @pytest.mark.asyncio
    async def test_create_and_get_campaign(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            create_resp = await ac.post(
                "/api/v1/campaigns",
                json={
                    "name": "Test Campaign",
                    "platform": "google_ads",
                    "status": "active",
                    "budget": 5000.0,
                },
            )
            if create_resp.status_code == 201:
                campaign_id = create_resp.json()["id"]
                get_resp = await ac.get(f"/api/v1/campaigns/{campaign_id}")
                assert get_resp.status_code == 200
                assert get_resp.json()["name"] == "Test Campaign"


class TestContactEndpoints:
    @pytest.mark.asyncio
    async def test_list_contacts(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.get("/api/v1/contacts")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data

    @pytest.mark.asyncio
    async def test_create_contact(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.post(
                "/api/v1/contacts",
                json={
                    "email": "integration@example.com",
                    "first_name": "Integration",
                    "last_name": "Test",
                    "source": "api",
                },
            )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "integration@example.com"

    @pytest.mark.asyncio
    async def test_facebook_lead_webhook(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.post(
                "/api/v1/contacts/webhook/facebook-lead",
                json={
                    "email": "lead@example.com",
                    "first_name": "Lead",
                    "last_name": "User",
                    "phone": "+15551234567",
                    "company": "Test Corp",
                },
            )
        assert response.status_code == 200
        data = response.json()
        assert "status" in data


class TestDashboardEndpoints:
    @pytest.mark.asyncio
    async def test_dashboard(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.get("/api/v1/dashboard")
        assert response.status_code == 200
        data = response.json()
        assert "overview" in data
        assert "top_campaigns" in data

    @pytest.mark.asyncio
    async def test_metrics(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.get("/api/v1/dashboard/metrics")
        assert response.status_code == 200


class TestNewsletterEndpoints:
    @pytest.mark.asyncio
    async def test_create_newsletter_campaign(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.post(
                "/api/v1/newsletter/campaigns",
                json={
                    "name": "Test Newsletter",
                    "subject": "Hello from Test",
                    "content": "<h1>Welcome</h1><p>Test content</p>",
                },
            )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Newsletter"
        assert data["subject"] == "Hello from Test"


class TestAutomationEndpoints:
    @pytest.mark.asyncio
    async def test_list_jobs(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.get("/api/v1/automation/jobs")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data

    @pytest.mark.asyncio
    async def test_job_stats(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.get("/api/v1/automation/jobs/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
