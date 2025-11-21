from uuid import UUID
from pydantic import BaseModel
from typing import Optional


class CountryBase(BaseModel):
    country_name: str


class CountryCreate(CountryBase):
    pass


class CountryUpdate(BaseModel):
    """All fields optional for partial updates"""
    country_name: Optional[str] = None


class Country(CountryBase):
    country_id: UUID

    class Config:
        from_attributes = True