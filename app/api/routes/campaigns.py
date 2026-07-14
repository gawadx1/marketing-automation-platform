from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.api.deps import get_db, get_campaign_repo
from app.schemas.campaign import CampaignCreate, CampaignUpdate, CampaignResponse, CampaignWithMetrics
from app.core.cache import cache_get, cache_set, cache_delete_pattern
from app.core.exceptions import NotFoundException

router = APIRouter(prefix="/campaigns", tags=["Campaigns"])


@router.get("", response_model=dict)
async def list_campaigns(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status: Optional[str] = None,
    platform: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    cache_key = f"campaigns:{skip}:{limit}:{status}:{platform}:{search}"
    cached = await cache_get(cache_key)
    if cached:
        return cached

    repo = await get_campaign_repo(db)
    filters = {}
    if status:
        filters["status"] = status
    if platform:
        filters["platform"] = platform

    campaigns, total = await repo.get_multi(
        skip=skip, limit=limit, filters=filters, order_by="created_at", descending=True
    )

    result = {
        "items": [CampaignResponse.model_validate(c).model_dump() for c in campaigns],
        "total": total,
        "skip": skip,
        "limit": limit,
    }
    await cache_set(cache_key, result, ttl=60)
    return result


@router.get("/{campaign_id}", response_model=CampaignWithMetrics)
async def get_campaign(campaign_id: int, db: AsyncSession = Depends(get_db)):
    repo = await get_campaign_repo(db)
    campaign, metrics = await repo.get_with_metrics(campaign_id)
    if not campaign:
        raise NotFoundException("Campaign", campaign_id)
    return CampaignWithMetrics(
        **CampaignResponse.model_validate(campaign).model_dump(),
        metrics=[m for m in metrics],
    )


@router.post("", response_model=CampaignResponse, status_code=201)
async def create_campaign(data: CampaignCreate, db: AsyncSession = Depends(get_db)):
    repo = await get_campaign_repo(db)
    campaign = await repo.create(**data.model_dump())
    await cache_delete_pattern("campaigns:*")
    return campaign


@router.put("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(campaign_id: int, data: CampaignUpdate, db: AsyncSession = Depends(get_db)):
    repo = await get_campaign_repo(db)
    campaign = await repo.update(campaign_id, **data.model_dump(exclude_none=True))
    if not campaign:
        raise NotFoundException("Campaign", campaign_id)
    await cache_delete_pattern("campaigns:*")
    return campaign


@router.delete("/{campaign_id}", status_code=204)
async def delete_campaign(campaign_id: int, db: AsyncSession = Depends(get_db)):
    repo = await get_campaign_repo(db)
    deleted = await repo.delete(campaign_id)
    if not deleted:
        raise NotFoundException("Campaign", campaign_id)
    await cache_delete_pattern("campaigns:*")
