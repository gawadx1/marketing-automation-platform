from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class NewsletterCreate(BaseModel):
    name: str
    subject: str
    content: str
    scheduled_at: Optional[datetime] = None


class NewsletterResponse(BaseModel):
    id: int
    name: str
    subject: str
    content: str
    status: str
    sent_count: int
    open_rate: float
    click_rate: float
    scheduled_at: Optional[datetime]
    sent_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NewsletterSendRequest(BaseModel):
    campaign_id: int
    contact_ids: Optional[list[int]] = None


class EmailEventResponse(BaseModel):
    id: int
    contact_id: int
    campaign_id: Optional[int]
    event_type: str
    occurred_at: datetime

    class Config:
        from_attributes = True
