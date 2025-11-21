from sqlalchemy import Column, String, Integer, DECIMAL, UniqueConstraint
from app.database import Base


class PricingDetail(Base):
    __tablename__ = "pricing_details"
    __table_args__ = (
        UniqueConstraint('country', 'role', 'band', name='unique_country_role_band'),
    )

    country = Column(String(50), primary_key=True)
    role = Column(String(100), primary_key=True)
    band = Column(Integer, primary_key=True)
    cost = Column(DECIMAL(12, 2))
    sale_price = Column(DECIMAL(12, 2))