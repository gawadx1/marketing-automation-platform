from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class CampaignBase(BaseModel):
    name: str
    platform: str
    status: str = "draft"
    budget: float = 0.0
    spent: float = 0.0
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    target_audience: Optional[str] = None


class CampaignCreate(CampaignBase):
    pass


class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None
    budget: Optional[float] = None
    spent: Optional[float] = None
    target_audience: Optional[str] = None


class CampaignResponse(CampaignBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CampaignMetricResponse(BaseModel):
    id: int
    campaign_id: int
    date: date
    impressions: int
    clicks: int
    conversions: int
    spend: float
    revenue: float
    leads: int
    ctr: float
    cpc: float
    cpa: float
    roas: float
    created_at: datetime

    class Config:
        from_attributes = True


class CampaignWithMetrics(CampaignResponse):
    metrics: list[CampaignMetricResponse] = []
