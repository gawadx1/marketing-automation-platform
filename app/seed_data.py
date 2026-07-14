"""Seed the database with demo data for development/testing."""

import asyncio
import random
from datetime import date, timedelta, datetime, timezone
from sqlalchemy import select, func
from app.core.database import get_session_factory, Base, get_engine
from app.core.security import get_password_hash
from app.models.user import User
from app.models.campaign import Campaign, CampaignPlatform, CampaignStatus
from app.models.campaign_metric import CampaignMetric
from app.models.contact import Contact, ContactSource, ContactStatus
from app.models.newsletter_campaign import NewsletterCampaign, NewsletterStatus
from app.models.email_event import EmailEvent, EmailEventType
from app.models.lead_event import LeadEvent, LeadStatus
from app.models.automation_job import AutomationJob, JobStatus
from loguru import logger

CAMPAIGN_NAMES = {
    CampaignPlatform.GOOGLE_ADS: [
        "Google Search - Brand",
        "Google Search - Generic",
        "Google Display - Retargeting",
        "Google Shopping - Products",
        "Google Video - Awareness",
    ],
    CampaignPlatform.META_ADS: [
        "Meta News Feed - Engagement",
        "Meta Stories - Branding",
        "Meta Lead Gen - Webinar",
        "Meta Retargeting - Sales",
        "Meta Video - Awareness",
    ],
    CampaignPlatform.HUBSPOT: [
        "HubSpot Email - Nurture",
        "HubSpot Blog - SEO",
        "HubSpot Landing Page - Conversion",
    ],
    CampaignPlatform.MAILCHIMP: [
        "Mailchimp Newsletter - Weekly",
        "Mailchimp Automation - Welcome",
    ],
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
    "Kate",
    "Liam",
    "Mia",
    "Noah",
    "Olivia",
    "Peter",
    "Quinn",
    "Rose",
    "Sam",
    "Tina",
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
    "Anderson",
    "Taylor",
    "Thomas",
    "Moore",
    "Jackson",
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
    "Oscorp",
    "Massive Dynamic",
]
CITIES = ["New York", "San Francisco", "Chicago", "Austin", "Seattle", "Boston", "Denver", "Portland", "Miami", "LA"]
COUNTRIES = ["US", "US", "US", "Canada", "UK", "Germany", "Australia"]


async def seed_database():
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = get_session_factory()
    async with factory() as db:
        existing = await db.scalar(select(func.count(User.id)))
        if existing and existing > 0:
            logger.info("Database already seeded, skipping")
            return

        logger.info("Seeding database with demo data...")

        admin = User(
            email="admin@platform.com",
            username="admin",
            hashed_password=get_password_hash("admin123"),
            full_name="System Administrator",
            is_active=True,
            is_superuser=True,
        )
        db.add(admin)
        await db.flush()
        logger.info(f"Created admin user (id={admin.id})")

        campaigns = []
        for platform, names in CAMPAIGN_NAMES.items():
            for name in names:
                status = random.choice(list(CampaignStatus))
                budget = random.uniform(1000, 50000)
                start = date.today() - timedelta(days=random.randint(30, 90))
                end = start + timedelta(days=random.randint(30, 60))
                campaign = Campaign(
                    name=name,
                    platform=platform,
                    status=status,
                    budget=round(budget, 2),
                    spent=0.0,
                    start_date=start,
                    end_date=end,
                )
                db.add(campaign)
                campaigns.append(campaign)
        await db.flush()
        logger.info(f"Created {len(campaigns)} campaigns")

        metrics = []
        for campaign in campaigns:
            if campaign.status == CampaignStatus.DRAFT:
                continue
            for days_ago in range(30):
                metric_date = date.today() - timedelta(days=days_ago)
                impressions = random.randint(1000, 50000)
                clicks = random.randint(int(impressions * 0.01), int(impressions * 0.08))
                conversions = random.randint(int(clicks * 0.03), int(clicks * 0.15))
                spend = round(random.uniform(50, 2000), 2)
                leads = random.randint(int(conversions * 0.5), conversions)
                revenue = round(spend * random.uniform(1.5, 5.0), 2)
                ctr = round(clicks / impressions * 100, 2) if impressions > 0 else 0
                cpc = round(spend / clicks, 2) if clicks > 0 else 0
                cpa = round(spend / conversions, 2) if conversions > 0 else 0
                roas = round(revenue / spend, 2) if spend > 0 else 0

                metric = CampaignMetric(
                    campaign_id=campaign.id,
                    date=metric_date,
                    impressions=impressions,
                    clicks=clicks,
                    conversions=conversions,
                    spend=spend,
                    revenue=revenue,
                    leads=leads,
                    ctr=ctr,
                    cpc=cpc,
                    cpa=cpa,
                    roas=roas,
                )
                db.add(metric)
                metrics.append(metric)

                campaign.spent = round(campaign.spent + spend, 2)
        await db.flush()
        logger.info(f"Created {len(metrics)} campaign metrics")

        contacts = []
        used_emails = set()
        for i in range(50):
            first = random.choice(FIRST_NAMES)
            last = random.choice(LAST_NAMES)
            email = f"{first.lower()}.{last.lower()}{i}@example.com"
            if email in used_emails:
                continue
            used_emails.add(email)
            contact = Contact(
                email=email,
                first_name=first,
                last_name=last,
                phone=f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
                company=random.choice(COMPANIES),
                source=random.choice(list(ContactSource)),
                status=random.choice(list(ContactStatus)),
                campaign_id=random.choice(campaigns).id if random.random() > 0.5 else None,
                score=random.randint(0, 100),
                city=random.choice(CITIES),
                country=random.choice(COUNTRIES),
            )
            db.add(contact)
            contacts.append(contact)
        await db.flush()
        logger.info(f"Created {len(contacts)} contacts")

        newsletters = []
        newsletter_data = [
            (
                "Weekly Digest",
                "Your Weekly Marketing Update",
                "<h1>Weekly Digest</h1><p>Here's what happened this week...</p>",
            ),
            ("Product Launch", "New Feature Release", "<h1>Big News!</h1><p>We're excited to announce...</p>"),
            (
                "Monthly Report",
                "Monthly Performance Summary",
                "<h1>Monthly Report</h1><p>Here's how we performed...</p>",
            ),
        ]
        for name, subject, content in newsletter_data:
            sent = random.randint(100, 5000)
            opens = int(sent * random.uniform(0.15, 0.35))
            clicks = int(opens * random.uniform(0.1, 0.3))
            nl = NewsletterCampaign(
                name=name,
                subject=subject,
                content=content,
                status=random.choice([NewsletterStatus.SENT, NewsletterStatus.DRAFT]),
                sent_count=sent,
                open_count=opens,
                click_count=clicks,
                open_rate=round(opens / sent * 100, 2),
                click_rate=round(clicks / sent * 100, 2),
                sent_at=datetime.now(timezone.utc) - timedelta(days=random.randint(1, 14)),
            )
            db.add(nl)
            newsletters.append(nl)
        await db.flush()
        logger.info(f"Created {len(newsletters)} newsletter campaigns")

        for contact in random.sample(contacts, min(20, len(contacts))):
            event_type = random.choice(list(EmailEventType))
            event = EmailEvent(
                contact_id=contact.id,
                campaign_id=random.choice(newsletters).id if newsletters else None,
                event_type=event_type,
                occurred_at=datetime.now(timezone.utc) - timedelta(days=random.randint(0, 14)),
                ip_address=f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}",
            )
            db.add(event)

        for contact in random.sample(contacts, min(10, len(contacts))):
            lead = LeadEvent(
                contact_id=contact.id,
                campaign_id=random.choice(campaigns).id if campaigns else None,
                source=random.choice(["facebook_lead_ads", "linkedin", "website_form", "webinar"]),
                status=random.choice(list(LeadStatus)),
                score=random.randint(0, 100),
                assigned_to=random.choice(["alice@company.com", "bob@company.com", "charlie@company.com"]),
            )
            db.add(lead)

        job_types = ["fetch_campaign_metrics", "fetch_contacts", "generate_report", "send_email", "cleanup_logs"]
        for _ in range(20):
            job = AutomationJob(
                job_type=random.choice(job_types),
                status=random.choice(list(JobStatus)),
                retry_count=random.randint(0, 3),
                max_retries=3,
                created_at=datetime.now(timezone.utc) - timedelta(hours=random.randint(0, 72)),
            )
            db.add(job)

        await db.commit()
        logger.info("Database seeding completed successfully!")


def main():
    asyncio.run(seed_database())


if __name__ == "__main__":
    main()
