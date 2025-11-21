from sqlalchemy import Column, String, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.database import Base


class StaffingDetail(Base):
    __tablename__ = "staffing_details"

    staffing_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    activity_id = Column(UUID(as_uuid=True), ForeignKey("activities.activity_id", ondelete="CASCADE"), nullable=False)
   
    country = Column(String(50))
    role = Column(String(100))
    band = Column(Integer)
    hours = Column(Integer)

    # Relationships
    activity = relationship("Activity", back_populates="staffing_details")
    # offering = relationship("Offering", back_populates="staffing_details")
 # offering_id = Column(UUID(as_uuid=True), ForeignKey("offerings.offering_id"), nullable=False)