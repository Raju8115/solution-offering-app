from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from uuid import UUID

from app.schemas.activity import ActivityWithRelation

class OfferingBase(BaseModel):
    offering_name: str
    saas_type: Optional[str] = None
    brand: Optional[str] = None
    supported_product: Optional[str] = None
    client_type: Optional[str] = None
    client_journey: Optional[str] = None
    client_journey_stage: Optional[str] = None
    framework_category: Optional[str] = None
    scenario: Optional[str] = None
    ibm_sales_play: Optional[str] = None
    tel_sales_tactic: Optional[str] = None
    industry: Optional[str] = None
    offering_tags: Optional[str] = None
    content_page: Optional[str] = None
    offering_sales_contact: Optional[str] = None
    offering_product_manager: Optional[str] = None
    offering_practice_leader: Optional[str] = None
    business_challenges: Optional[str] = None
    business_drivers: Optional[str] = None
    offering_value: Optional[str] = None
    tag_line: Optional[str] = None
    elevator_pitch: Optional[str] = None
    offering_outcomes: Optional[str] = None
    key_deliverables: Optional[str] = None
    offering_summary: Optional[str] = None
    when_and_why_to_sell: Optional[str] = None
    buyer_persona: Optional[str] = None
    user_persona: Optional[str] = None
    scope_summary: Optional[str] = None
    duration: Optional[str] = None
    occ: Optional[str] = None
    prerequisites: Optional[str] = None
    seismic_link: Optional[str] = None
    part_numbers: Optional[str] = None

class OfferingCreate(OfferingBase):
    product_id: UUID


class OfferingUpdate(BaseModel):
    """All fields optional for partial updates"""
    offering_name: Optional[str] = None
    saas_type: Optional[str] = None
    brand: Optional[str] = None
    supported_product: Optional[str] = None
    client_type: Optional[str] = None
    client_journey: Optional[str] = None
    client_journey_stage: Optional[str] = None
    framework_category: Optional[str] = None
    scenario: Optional[str] = None
    ibm_sales_play: Optional[str] = None
    tel_sales_tactic: Optional[str] = None
    industry: Optional[str] = None
    offering_tags: Optional[str] = None
    content_page: Optional[str] = None
    offering_sales_contact: Optional[str] = None
    offering_product_manager: Optional[str] = None
    offering_practice_leader: Optional[str] = None
    business_challenges: Optional[str] = None
    business_drivers: Optional[str] = None
    offering_value: Optional[str] = None
    tag_line: Optional[str] = None
    elevator_pitch: Optional[str] = None
    offering_outcomes: Optional[str] = None
    key_deliverables: Optional[str] = None
    offering_summary: Optional[str] = None
    when_and_why_to_sell: Optional[str] = None
    buyer_persona: Optional[str] = None
    user_persona: Optional[str] = None
    scope_summary: Optional[str] = None
    duration: Optional[str] = None
    occ: Optional[str] = None
    prerequisites: Optional[str] = None
    seismic_link: Optional[str] = None
    part_numbers: Optional[str] = None
    product_id: Optional[UUID] = None


class Offering(OfferingBase):
    offering_id: UUID
    product_id: UUID
    created_on: Optional[datetime] = None
    updated_on: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class OfferingWithActivities(Offering):
    activities: List['ActivityWithRelation'] = []
    
    class Config:
        from_attributes = True


class OfferingSearch(BaseModel):
    query: Optional[str] = None
    saas_type: Optional[str] = None
    industry: Optional[str] = None
    client_type: Optional[str] = None
    framework_category: Optional[str] = None