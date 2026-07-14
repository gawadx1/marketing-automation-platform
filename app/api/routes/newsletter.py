from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db
from app.schemas.newsletter import NewsletterCreate, NewsletterResponse, NewsletterSendRequest
from app.repositories.base import BaseRepository
from app.models.newsletter_campaign import NewsletterCampaign, NewsletterStatus
from app.models.contact import Contact
from app.workers.tasks import send_email_task
from app.core.exceptions import NotFoundException

router = APIRouter(prefix="/newsletter", tags=["Newsletter"])


@router.post("/send", response_model=dict)
async def send_newsletter(request: NewsletterSendRequest, db: AsyncSession = Depends(get_db)):
    repo = BaseRepository(NewsletterCampaign, db)
    campaign = await repo.get(request.campaign_id)
    if not campaign:
        raise NotFoundException("Newsletter campaign", request.campaign_id)

    contact_repo = BaseRepository(Contact, db)
    if request.contact_ids:
        contacts = []
        for cid in request.contact_ids:
            c = await contact_repo.get(cid)
            if c:
                contacts.append(c)
    else:
        contacts, _ = await contact_repo.get_multi(limit=5000, filters={"status": "subscribed"})

    for contact in contacts:
        send_email_task.delay(
            contact_id=contact.id,
            email=contact.email,
            subject=campaign.subject,
            content=campaign.content,
            campaign_id=campaign.id,
        )

    await repo.update(campaign.id, status=NewsletterStatus.SENDING)

    return {
        "status": "queued",
        "campaign_id": campaign.id,
        "total_recipients": len(contacts),
    }


@router.post("/campaigns", response_model=NewsletterResponse, status_code=201)
async def create_newsletter_campaign(data: NewsletterCreate, db: AsyncSession = Depends(get_db)):
    repo = BaseRepository(NewsletterCampaign, db)
    campaign = await repo.create(**data.model_dump())
    return campaign


@router.get("/campaigns", response_model=dict)
async def list_newsletter_campaigns(db: AsyncSession = Depends(get_db)):
    repo = BaseRepository(NewsletterCampaign, db)
    campaigns, total = await repo.get_multi(order_by="created_at", descending=True)
    return {
        "items": [NewsletterResponse.model_validate(c).model_dump() for c in campaigns],
        "total": total,
    }


@router.get("/campaigns/{campaign_id}", response_model=NewsletterResponse)
async def get_newsletter_campaign(campaign_id: int, db: AsyncSession = Depends(get_db)):
    repo = BaseRepository(NewsletterCampaign, db)
    campaign = await repo.get(campaign_id)
    if not campaign:
        raise NotFoundException("Newsletter campaign", campaign_id)
    return campaign
