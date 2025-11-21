from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.database import Base


class Product(Base):
    __tablename__ = "products"

    product_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    brand_id = Column(UUID(as_uuid=True), ForeignKey("brands.brand_id", ondelete="CASCADE"), nullable=False)
    product_name = Column(String(255), nullable=False)
    description = Column(Text)

    # Relationships
    brand = relationship("Brand", back_populates="products")
    offerings = relationship("Offering", back_populates="product", cascade="all, delete-orphan")
