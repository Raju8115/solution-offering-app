from pydantic import BaseModel
from uuid import UUID
from typing import Optional


class WBSBase(BaseModel):
    wbs_description: str
    wbs_weeks: Optional[int] = None


class WBSCreate(WBSBase):
    pass


class WBSUpdate(BaseModel):
    wbs_description: Optional[str] = None
    wbs_weeks: Optional[int] = None


class WBSResponse(WBSBase):
    wbs_id: UUID

    class Config:
        from_attributes = True


class ActivityWBSCreate(BaseModel):
    activity_id: UUID
    wbs_id: UUID


class ActivityWBSResponse(BaseModel):
    activity_id: UUID
    wbs_id: UUID

    class Config:
        from_attributes = True