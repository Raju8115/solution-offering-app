from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.database import Base


class Country(Base):
    __tablename__ = "countries"

    country_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    country_name = Column(String(100), unique=True, nullable=False)
