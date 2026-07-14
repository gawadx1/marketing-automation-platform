from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AutomationJobResponse(BaseModel):
    id: int
    job_type: str
    status: str
    payload: Optional[str]
    result: Optional[str]
    retry_count: int
    max_retries: int
    error_message: Optional[str]
    scheduled_at: Optional[datetime]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class HealthResponse(BaseModel):
    status: str
    version: str
    database: str
    redis: str
    celery: str
    uptime_seconds: float
