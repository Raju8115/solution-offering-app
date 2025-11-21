from sqlalchemy.orm import Session
from app.models.staffing import StaffingDetail
from app.models.activity import Activity
from app.models.activity import OfferingActivity
from app.schemas.staffing import StaffingDetailCreate, StaffingDetailUpdate
from typing import List, Optional
import uuid


def get_all_staffing(db: Session) -> List[StaffingDetail]:
    """Get all staffing details"""
    return db.query(StaffingDetail).all()


def get_staffing_by_offering(db: Session, offering_id: str) -> List[StaffingDetail]:
    """Get all staffing details for a specific offering"""
    return (
        db.query(StaffingDetail)
        .join(Activity, StaffingDetail.activity_id == Activity.activity_id)
        .join(OfferingActivity, OfferingActivity.activity_id == Activity.activity_id)
        .filter(OfferingActivity.offering_id == offering_id)
        .all()
    )


def get_staffing_by_id(db: Session, staffing_id: str) -> Optional[StaffingDetail]:
    """Get a single staffing detail by ID"""
    return db.query(StaffingDetail).filter(StaffingDetail.staffing_id == staffing_id).first()


def get_staffing_by_activity(db: Session, activity_id: str) -> List[StaffingDetail]:
    """Get all staffing details for a specific activity"""
    return db.query(StaffingDetail).filter(StaffingDetail.activity_id == activity_id).all()


def create_staffing_detail(db: Session, staffing: StaffingDetailCreate) -> StaffingDetail:
    """Create a new staffing detail"""
    db_staffing = StaffingDetail(
        staffing_id=uuid.uuid4(),
        activity_id=staffing.activity_id,
        country=staffing.country,
        role=staffing.role,
        band=staffing.band,
        hours=staffing.hours
    )
    db.add(db_staffing)
    db.commit()
    db.refresh(db_staffing)
    return db_staffing


def update_staffing_detail(
    db: Session, 
    staffing_id: str, 
    staffing: StaffingDetailUpdate
) -> Optional[StaffingDetail]:
    """Update an existing staffing detail"""
    db_staffing = db.query(StaffingDetail).filter(
        StaffingDetail.staffing_id == staffing_id
    ).first()
    
    if not db_staffing:
        return None
    
    update_data = staffing.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_staffing, field, value)
    
    db.commit()
    db.refresh(db_staffing)
    return db_staffing


def delete_staffing_detail(db: Session, staffing_id: str) -> bool:
    """Delete a staffing detail"""
    db_staffing = db.query(StaffingDetail).filter(
        StaffingDetail.staffing_id == staffing_id
    ).first()
    
    if not db_staffing:
        return False
    
    db.delete(db_staffing)
    db.commit()
    return True