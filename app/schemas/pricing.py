from pydantic import BaseModel
from typing import Optional
from decimal import Decimal


class PricingDetailBase(BaseModel):
    country: str
    role: str
    band: int
    cost: Optional[Decimal] = None
    sale_price: Optional[Decimal] = None


class PricingDetailCreate(PricingDetailBase):
    pass


class PricingDetailUpdate(BaseModel):
    """All fields optional for partial updates"""
    country: Optional[str] = None
    role: Optional[str] = None
    band: Optional[int] = None
    cost: Optional[Decimal] = None
    sale_price: Optional[Decimal] = None


class PricingDetail(PricingDetailBase):

    class Config:
        from_attributes = True