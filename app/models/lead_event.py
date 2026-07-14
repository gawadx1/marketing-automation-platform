from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, func
from app.core.database import Base
from sqlalchemy import Enum as SAEnum
import enum


class LeadStatus(str, enum.Enum):
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    CONVERTED = "converted"
    LOST = "lost"


class LeadEvent(Base):
    __tablename__ = "lead_events"

    id = Column(Integer, primary_key=True, index=True)
    contact_id = Column(
        Integer,
        ForeignKey("contacts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    campaign_id = Column(Integer, ForeignKey("campaigns.id", ondelete="SET NULL"))
    source = Column(String(100), nullable=False)
    status = Column(SAEnum(LeadStatus), default=LeadStatus.NEW)
    score = Column(Integer, default=0)
    assigned_to = Column(String(255))
    notes = Column(Text)
    payload = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
