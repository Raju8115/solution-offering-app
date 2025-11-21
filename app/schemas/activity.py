from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from uuid import UUID

class ActivityBase(BaseModel):
    activity_name: str
    brand: Optional[str] = None
    product_name: Optional[str] = None
    category: Optional[str] = None
    part_numbers: Optional[str] = None
    duration_weeks: Optional[int] = None
    duration_hours: Optional[int] = None
    outcome: Optional[str] = None
    description: Optional[str] = None
    effort_hours: Optional[int] = None
    fixed_price: Optional[Decimal] = None
    client_responsibilities: Optional[str] = None
    ibm_responsibilities: Optional[str] = None
    assumptions: Optional[str] = None
    deliverables: Optional[str] = None
    completion_criteria: Optional[str] = None
    wbs: Optional[str] = None
    week: Optional[int] = None

class ActivityCreate(ActivityBase):
    """Schema for creating a new activity (standalone)"""
    pass

class ActivityUpdate(BaseModel):
    """Schema for updating an activity (all fields optional)"""
    activity_name: Optional[str] = None
    brand: Optional[str] = None
    product_name: Optional[str] = None
    category: Optional[str] = None
    part_numbers: Optional[str] = None
    duration_weeks: Optional[int] = None
    duration_hours: Optional[int] = None
    outcome: Optional[str] = None
    description: Optional[str] = None
    effort_hours: Optional[int] = None
    fixed_price: Optional[Decimal] = None
    client_responsibilities: Optional[str] = None
    ibm_responsibilities: Optional[str] = None
    assumptions: Optional[str] = None
    deliverables: Optional[str] = None
    completion_criteria: Optional[str] = None
    wbs: Optional[str] = None
    week: Optional[int] = None

class Activity(ActivityBase):
    """Schema for activity response"""
    activity_id: UUID
    created_on: Optional[datetime] = None
    updated_on: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class ActivityWithRelation(Activity):
    """Activity with offering-specific fields"""
    sequence: Optional[int] = None
    is_mandatory: Optional[bool] = None

class ActivityWithOfferings(Activity):
    """Activity with list of offerings using it"""
    offerings: List[dict] = []

# Offering-Activity Junction Schemas
class OfferingActivityBase(BaseModel):
    offering_id: UUID
    activity_id: UUID
    sequence: Optional[int] = None
    is_mandatory: bool = True

class OfferingActivityCreate(OfferingActivityBase):
    """Schema for linking an activity to an offering"""
    pass

class OfferingActivityUpdate(BaseModel):
    """Schema for updating offering-activity relationship"""
    sequence: Optional[int] = None
    is_mandatory: Optional[bool] = None

class OfferingActivity(OfferingActivityBase):
    created_on: Optional[datetime] = None
    
    class Config:
        from_attributes = True