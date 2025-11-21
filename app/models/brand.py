from sqlalchemy import Column, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.database import Base


class Brand(Base):
    __tablename__ = "brands"

    brand_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    brand_name = Column(String(255), unique=True, nullable=False)
    description = Column(Text)

    # Relationships
    products = relationship("Product", back_populates="brand", cascade="all, delete-orphan")
