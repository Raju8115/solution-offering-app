from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class ProductBase(BaseModel):
    product_name: str
    description: Optional[str] = None
    brand_id: UUID


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    """All fields optional for partial updates"""
    product_name: Optional[str] = None
    description: Optional[str] = None
    brand_id: Optional[UUID] = None


class Product(ProductBase):
    product_id: UUID

    class Config:
        from_attributes = True