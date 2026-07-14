import json
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.contact import ContactRepository, LeadEventRepository
from app.models.contact import ContactSource, ContactStatus
from app.models.lead_event import LeadStatus
from app.schemas.contact import LeadWebhookPayload
from app.workers.tasks import notify_sales_team
from loguru import logger


class WebhookProcessor:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.contact_repo = ContactRepository(db)
        self.lead_repo = LeadEventRepository(db)

    async def process_facebook_lead(self, payload: LeadWebhookPayload) -> dict:
        logger.info(f"Processing Facebook lead webhook: {payload.email}")

        existing = await self.contact_repo.get_by_email(payload.email)
        if existing:
            contact = existing
            logger.info(f"Existing contact found: {contact.id}")
        else:
            contact = await self.contact_repo.create(
                email=payload.email,
                first_name=payload.first_name,
                last_name=payload.last_name,
                phone=payload.phone,
                company=payload.company,
                source=ContactSource.LEAD_FORM,
                status=ContactStatus.SUBSCRIBED,
                campaign_id=payload.campaign_id,
            )
            logger.info(f"New contact created: {contact.id}")

        lead_event = await self.lead_repo.create(
            contact_id=contact.id,
            campaign_id=payload.campaign_id,
            source="facebook_lead_ads",
            status=LeadStatus.NEW,
            score=50,
            payload=payload.model_dump_json(),
        )
        logger.info(f"Lead event created: {lead_event.id}")

        notify_sales_team.delay(
            contact_id=contact.id,
            lead_event_id=lead_event.id,
            email=payload.email,
            name=f"{payload.first_name} {payload.last_name}".strip(),
        )

        return {
            "status": "success",
            "contact_id": contact.id,
            "lead_event_id": lead_event.id,
        }

    async def process_mailchimp_webhook(self, event_type: str, data: dict) -> dict:
        logger.info(f"Processing Mailchimp webhook: {event_type}")
        email = data.get("email", "")
        contact = await self.contact_repo.get_by_email(email)

        if not contact:
            logger.warning(f"Contact not found for Mailchimp webhook: {email}")
            return {"status": "ignored", "reason": "contact_not_found"}

        event_map = {
            "subscribe": ContactStatus.SUBSCRIBED,
            "unsubscribe": ContactStatus.UNSUBSCRIBED,
            "cleaned": ContactStatus.BOUNCED,
        }

        if event_type in event_map:
            await self.contact_repo.update(contact.id, status=event_map[event_type])

        return {
            "status": "processed",
            "event_type": event_type,
            "contact_id": contact.id,
        }
