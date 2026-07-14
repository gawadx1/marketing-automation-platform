from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.api.deps import get_db, get_contact_repo
from app.schemas.contact import ContactCreate, ContactUpdate, ContactResponse, LeadWebhookPayload
from app.integrations.webhooks import WebhookProcessor
from app.core.exceptions import NotFoundException, DuplicateException

router = APIRouter(prefix="/contacts", tags=["Contacts"])


@router.get("", response_model=dict)
async def list_contacts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status: Optional[str] = None,
    source: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    repo = await get_contact_repo(db)
    if search:
        contacts, total = await repo.search(search, skip=skip, limit=limit)
    else:
        filters = {}
        if status:
            filters["status"] = status
        if source:
            filters["source"] = source
        contacts, total = await repo.get_multi(
            skip=skip, limit=limit, filters=filters, order_by="created_at", descending=True
        )
    return {
        "items": [ContactResponse.model_validate(c).model_dump() for c in contacts],
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(contact_id: int, db: AsyncSession = Depends(get_db)):
    repo = await get_contact_repo(db)
    contact = await repo.get(contact_id)
    if not contact:
        raise NotFoundException("Contact", contact_id)
    return contact


@router.post("", response_model=ContactResponse, status_code=201)
async def create_contact(data: ContactCreate, db: AsyncSession = Depends(get_db)):
    repo = await get_contact_repo(db)
    existing = await repo.get_by_email(data.email)
    if existing:
        raise DuplicateException("Contact", "email", data.email)
    contact = await repo.create(**data.model_dump())
    return contact


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(contact_id: int, data: ContactUpdate, db: AsyncSession = Depends(get_db)):
    repo = await get_contact_repo(db)
    contact = await repo.update(contact_id, **data.model_dump(exclude_none=True))
    if not contact:
        raise NotFoundException("Contact", contact_id)
    return contact


@router.delete("/{contact_id}", status_code=204)
async def delete_contact(contact_id: int, db: AsyncSession = Depends(get_db)):
    repo = await get_contact_repo(db)
    deleted = await repo.delete(contact_id)
    if not deleted:
        raise NotFoundException("Contact", contact_id)


@router.post("/webhook/facebook-lead")
async def facebook_lead_webhook(payload: LeadWebhookPayload, db: AsyncSession = Depends(get_db)):
    processor = WebhookProcessor(db)
    result = await processor.process_facebook_lead(payload)
    return result
