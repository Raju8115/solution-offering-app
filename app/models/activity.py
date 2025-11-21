from sqlalchemy import Column, ForeignKey, String, Text, Integer, Boolean, DECIMAL, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid


class Activity(Base):
    __tablename__ = "activities"
    
    activity_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    activity_name = Column(String(255), nullable=False)
    brand = Column(String(150)) #1
    product_name = Column(String(255)) #1
    category = Column(String(100))
    part_numbers = Column(String(100))
    duration_weeks = Column(Integer)
    duration_hours = Column(Integer)
    outcome = Column(Text)
    description = Column(Text)
    effort_hours = Column(Integer)
    fixed_price = Column(DECIMAL(12, 2))
    client_responsibilities = Column(Text)
    ibm_responsibilities = Column(Text)
    assumptions = Column(Text)
    deliverables = Column(Text)
    completion_criteria = Column(Text)
    wbs = Column(String(100))
    week = Column(Integer)
    created_on = Column(TIMESTAMP, server_default=func.now())
    updated_on = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    offerings = relationship(
    "OfferingActivity", 
    back_populates="activity",
    cascade="all, delete-orphan",
    passive_deletes=True
    )
    staffing_details = relationship(
        "StaffingDetail", 
        back_populates="activity",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    wbs_entries = relationship(
        "ActivityWBS", 
        back_populates="activity",
        cascade="all, delete-orphan",
        passive_deletes=True
    )


class OfferingActivity(Base):
    """Junction table for many-to-many relationship between offerings and activities"""
    __tablename__ = "offering_activities"
    
    offering_id = Column(UUID(as_uuid=True), ForeignKey("offerings.offering_id", ondelete="CASCADE"), primary_key=True)
    activity_id = Column(UUID(as_uuid=True), ForeignKey("activities.activity_id", ondelete="CASCADE"), primary_key=True)
    sequence = Column(Integer)
    is_mandatory = Column(Boolean, default=True)
    created_on = Column(TIMESTAMP, server_default=func.now())
    
    # Relationships
    offering = relationship("Offering", back_populates="activities")
    activity = relationship("Activity", back_populates="offerings")
