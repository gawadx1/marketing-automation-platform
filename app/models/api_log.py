from sqlalchemy import Column, Integer, String, Float, DateTime, Text, func
from app.core.database import Base


class ApiLog(Base):
    __tablename__ = "api_logs"

    id = Column(Integer, primary_key=True, index=True)
    endpoint = Column(String(500), nullable=False, index=True)
    method = Column(String(10), nullable=False)
    status_code = Column(Integer)
    response_time_ms = Column(Float)
    request_body = Column(Text)
    response_body = Column(Text)
    ip_address = Column(String(50))
    user_id = Column(String(100))
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
