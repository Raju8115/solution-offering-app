from sqlalchemy import Column, String, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.database import Base


class WBS(Base):
    __tablename__ = "wbs"
    
    wbs_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    wbs_description = Column(String(255), nullable=False)
    wbs_weeks = Column(Integer)
    
    # Relationships
    activities = relationship(
    "ActivityWBS", 
    back_populates="wbs",
    cascade="all, delete-orphan",
    passive_deletes=True
)