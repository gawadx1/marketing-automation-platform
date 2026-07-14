from sqlalchemy import Column, Integer, String, DateTime, Text, BigInteger, func
from app.core.database import Base


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(BigInteger, primary_key=True, index=True)
    action = Column(String(100), nullable=False, index=True)
    entity_type = Column(String(50), index=True)
    entity_id = Column(Integer)
    user_id = Column(Integer, index=True)
    details = Column(Text)
    ip_address = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
