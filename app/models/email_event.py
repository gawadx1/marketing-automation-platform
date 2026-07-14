from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, func
from app.core.database import Base
from sqlalchemy import Enum as SAEnum
import enum


class EmailEventType(str, enum.Enum):
    SENT = "sent"
    OPENED = "opened"
    CLICKED = "clicked"
    BOUNCED = "bounced"
    UNSUBSCRIBED = "unsubscribed"
    COMPLAINED = "complained"


class EmailEvent(Base):
    __tablename__ = "email_events"

    id = Column(Integer, primary_key=True, index=True)
    contact_id = Column(
        Integer,
        ForeignKey("contacts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    campaign_id = Column(
        Integer, ForeignKey("newsletter_campaigns.id", ondelete="SET NULL")
    )
    event_type = Column(SAEnum(EmailEventType), nullable=False)
    metadata_json = Column(Text)
    ip_address = Column(String(50))
    user_agent = Column(String(500))
    occurred_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
