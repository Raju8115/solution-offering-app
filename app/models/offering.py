from sqlalchemy import DECIMAL, Column, String, Text, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid


class Offering(Base):
    __tablename__ = "offerings"

    offering_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.product_id", ondelete="CASCADE"), nullable=False)

    offering_name = Column(String(255), nullable=False)
    saas_type = Column(String(100))
    brand = Column(String(255))
    supported_product = Column(String(255))
    client_type = Column(String(255))
    client_journey = Column(String(255))
    client_journey_stage = Column(String(255))
    framework_category = Column(String(255))
    scenario = Column(String(255))
    ibm_sales_play = Column(String(255))
    tel_sales_tactic = Column(String(255))
    industry = Column(String(255))
    offering_tags = Column(Text)              # was String(255)
    content_page = Column(Text)               # was String(255)
    offering_sales_contact = Column(String(255))
    offering_product_manager = Column(String(255))
    offering_practice_leader = Column(String(255))
    business_challenges = Column(Text)
    business_drivers = Column(Text)
    offering_value = Column(Text)
    tag_line = Column(Text)
    elevator_pitch = Column(Text)
    offering_outcomes = Column(Text)
    key_deliverables = Column(Text)
    offering_summary = Column(Text)
    when_and_why_to_sell = Column(Text)
    buyer_persona = Column(Text)
    user_persona = Column(Text)
    scope_summary = Column(Text)
    duration = Column(String(50))
    occ = Column(Text)
    prerequisites = Column(Text)
    seismic_link = Column(Text)
    part_numbers = Column(String(100))
    sale_price = Column(DECIMAL(12, 2))

    created_on = Column(TIMESTAMP, server_default=func.now())
    updated_on = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    product = relationship("Product", back_populates="offerings")
    activities = relationship(
        "OfferingActivity", 
        back_populates="offering",
        cascade="all, delete-orphan", 
        passive_deletes=True 
    )
    # staffing_details = relationship("StaffingDetail", back_populates="offering")
