from sqlalchemy import Column, Integer, String, Float, DateTime, Text, func
from app.core.database import Base
from sqlalchemy import Enum as SAEnum
import enum


class NewsletterStatus(str, enum.Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    SENDING = "sending"
    SENT = "sent"
    FAILED = "failed"


class NewsletterCampaign(Base):
    __tablename__ = "newsletter_campaigns"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    subject = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    status = Column(SAEnum(NewsletterStatus), default=NewsletterStatus.DRAFT)
    sent_count = Column(Integer, default=0)
    open_count = Column(Integer, default=0)
    click_count = Column(Integer, default=0)
    open_rate = Column(Float, default=0.0)
    click_rate = Column(Float, default=0.0)
    scheduled_at = Column(DateTime(timezone=True))
    sent_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
