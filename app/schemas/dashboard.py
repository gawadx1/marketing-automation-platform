from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class DashboardStats(BaseModel):
    today_spend: float = 0.0
    today_clicks: int = 0
    today_impressions: int = 0
    today_leads: int = 0
    today_conversions: int = 0
    total_campaigns: int = 0
    active_campaigns: int = 0
    total_contacts: int = 0


class CampaignPerformance(BaseModel):
    id: int
    name: str
    platform: str
    status: str
    spend: float
    impressions: int
    clicks: int
    conversions: int
    ctr: float
    cpc: float
    cpa: float


class DailyStats(BaseModel):
    date: date
    spend: float
    clicks: int
    impressions: int
    conversions: int
    leads: int


class DashboardResponse(BaseModel):
    overview: DashboardStats
    top_campaigns: list[CampaignPerformance] = []
    daily_stats: list[DailyStats] = []
    weekly_growth: float = 0.0
    monthly_growth: float = 0.0
    last_updated: datetime


class DailyReport(BaseModel):
    report_date: date
    total_spend: float
    total_clicks: int
    total_impressions: int
    total_conversions: int
    total_leads: int
    ctr: float
    cpc: float
    cpa: float
    top_campaign: Optional[str]
    worst_campaign: Optional[str]
    generated_at: datetime
