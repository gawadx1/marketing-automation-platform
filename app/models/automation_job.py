from sqlalchemy import Column, Integer, String, DateTime, Text, func
from app.core.database import Base
from sqlalchemy import Enum as SAEnum
import enum


class JobStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


class AutomationJob(Base):
    __tablename__ = "automation_jobs"

    id = Column(Integer, primary_key=True, index=True)
    job_type = Column(String(100), nullable=False, index=True)
    status = Column(SAEnum(JobStatus), default=JobStatus.PENDING, index=True)
    payload = Column(Text)
    result = Column(Text)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    error_message = Column(Text)
    scheduled_at = Column(DateTime(timezone=True))
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
