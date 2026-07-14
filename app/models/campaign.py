from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Text, func
from app.core.database import Base
from sqlalchemy import Enum as SAEnum
import enum


class CampaignStatus(str, enum.Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    DRAFT = "draft"
    ARCHIVED = "archived"


class CampaignPlatform(str, enum.Enum):
    GOOGLE_ADS = "google_ads"
    META_ADS = "meta_ads"
    HUBSPOT = "hubspot"
    MAILCHIMP = "mailchimp"


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    platform = Column(SAEnum(CampaignPlatform), nullable=False)
    status = Column(SAEnum(CampaignStatus), default=CampaignStatus.DRAFT)
    budget = Column(Float, default=0.0)
    spent = Column(Float, default=0.0)
    start_date = Column(Date)
    end_date = Column(Date)
    target_audience = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
