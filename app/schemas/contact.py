from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class ContactBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = ""
    last_name: Optional[str] = ""
    phone: Optional[str] = ""
    company: Optional[str] = ""
    source: str = "manual"
    status: str = "pending"
    campaign_id: Optional[int] = None
    city: Optional[str] = ""
    country: Optional[str] = ""


class ContactCreate(ContactBase):
    pass


class ContactUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    status: Optional[str] = None
    campaign_id: Optional[int] = None
    score: Optional[int] = None


class ContactResponse(ContactBase):
    id: int
    score: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LeadEventResponse(BaseModel):
    id: int
    contact_id: int
    campaign_id: Optional[int]
    source: str
    status: str
    score: int
    assigned_to: Optional[str]
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class LeadWebhookPayload(BaseModel):
    email: str
    first_name: str = ""
    last_name: str = ""
    phone: str = ""
    company: str = ""
    campaign_id: Optional[int] = None
    form_id: Optional[str] = None
    ad_id: Optional[str] = None
    page_url: Optional[str] = None
