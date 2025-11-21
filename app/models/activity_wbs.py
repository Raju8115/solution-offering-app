from sqlalchemy import Column, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class ActivityWBS(Base):
    """Junction table for many-to-many relationship between activities and WBS"""
    __tablename__ = "activity_wbs"
    
    activity_id = Column(UUID(as_uuid=True), ForeignKey("activities.activity_id", ondelete="CASCADE"), primary_key=True)
    wbs_id = Column(UUID(as_uuid=True), ForeignKey("wbs.wbs_id", ondelete="CASCADE"), primary_key=True)
    created_on = Column(TIMESTAMP, server_default=func.now())
    
    # Relationships
    activity = relationship("Activity", back_populates="wbs_entries")
    wbs = relationship("WBS", back_populates="activities")