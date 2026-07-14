from sqlalchemy import Column, Integer, Float, DateTime, Date, ForeignKey, func
from app.core.database import Base


class CampaignMetric(Base):
    __tablename__ = "campaign_metrics"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(
        Integer,
        ForeignKey("campaigns.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    date = Column(Date, nullable=False, index=True)
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    conversions = Column(Integer, default=0)
    spend = Column(Float, default=0.0)
    revenue = Column(Float, default=0.0)
    leads = Column(Integer, default=0)
    ctr = Column(Float, default=0.0)
    cpc = Column(Float, default=0.0)
    cpa = Column(Float, default=0.0)
    roas = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
