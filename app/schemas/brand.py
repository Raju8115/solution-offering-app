from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class BrandBase(BaseModel):
    brand_name: str
    description: Optional[str] = None


class BrandCreate(BrandBase):
    pass


class BrandUpdate(BaseModel):
    """All fields optional for partial updates"""
    brand_name: Optional[str] = None
    description: Optional[str] = None


class Brand(BrandBase):
    brand_id: UUID

    class Config:
        from_attributes = True