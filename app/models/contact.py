from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from app.core.database import Base
from sqlalchemy import Enum as SAEnum
import enum


class ContactStatus(str, enum.Enum):
    SUBSCRIBED = "subscribed"
    UNSUBSCRIBED = "unsubscribed"
    BOUNCED = "bounced"
    PENDING = "pending"


class ContactSource(str, enum.Enum):
    MANUAL = "manual"
    HUBSPOT = "hubspot"
    MAILCHIMP = "mailchimp"
    LEAD_FORM = "lead_form"
    API = "api"


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    phone = Column(String(50))
    company = Column(String(255))
    source = Column(SAEnum(ContactSource), default=ContactSource.MANUAL)
    status = Column(SAEnum(ContactStatus), default=ContactStatus.PENDING)
    campaign_id = Column(Integer, ForeignKey("campaigns.id", ondelete="SET NULL"))
    score = Column(Integer, default=0)
    city = Column(String(100))
    country = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
