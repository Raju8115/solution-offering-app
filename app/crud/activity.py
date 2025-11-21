from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from app.models.activity import Activity, OfferingActivity
from app.schemas.activity import ActivityCreate, ActivityUpdate, OfferingActivityCreate
from typing import List, Optional

def get_all_activities(db: Session, skip: int = 0, limit: int = 100) -> List[Activity]:
    """Get all activities regardless of offering association"""
    return db.query(Activity).offset(skip).limit(limit).all()

def get_activities_by_offering(db: Session, offering_id: str) -> List[dict]:
    """Get all activities for a specific offering with relationship data"""
    results = db.query(Activity, OfferingActivity).join(
        OfferingActivity, Activity.activity_id == OfferingActivity.activity_id
    ).filter(
        OfferingActivity.offering_id == offering_id
    ).order_by(
        OfferingActivity.sequence
    ).all()
    
    activities = []
    for activity, offering_activity in results:
        activity_dict = {
            "activity_id": activity.activity_id,
            "activity_name": activity.activity_name,
            "brand": activity.brand,
            "product_name": activity.product_name,
            "category": activity.category,
            "part_numbers": activity.part_numbers,
            "duration_weeks": activity.duration_weeks,
            "duration_hours": activity.duration_hours,
            "outcome": activity.outcome,
            "description": activity.description,
            "effort_hours": activity.effort_hours,
            "fixed_price": activity.fixed_price,
            "client_responsibilities": activity.client_responsibilities,
            "ibm_responsibilities": activity.ibm_responsibilities,
            "assumptions": activity.assumptions,
            "deliverables": activity.deliverables,
            "completion_criteria": activity.completion_criteria,
            "wbs": activity.wbs,
            "week": activity.week,
            "created_on": activity.created_on,
            "updated_on": activity.updated_on,
            # Offering-specific fields from junction table
            "sequence": offering_activity.sequence,
            "is_mandatory": offering_activity.is_mandatory
        }
        activities.append(activity_dict)
    
    return activities

def get_unassigned_activities(db: Session) -> List[Activity]:
    """Get activities that are not assigned to any offering"""
    subquery = db.query(OfferingActivity.activity_id).distinct()
    return db.query(Activity).filter(
        ~Activity.activity_id.in_(subquery)
    ).all()

def get_activity_by_id(db: Session, activity_id: str) -> Optional[Activity]:
    """Get a single activity by ID"""
    return db.query(Activity).filter(Activity.activity_id == activity_id).first()

def create_activity(db: Session, activity: ActivityCreate) -> Activity:
    """Create a new standalone activity"""
    db_activity = Activity(**activity.dict())
    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)
    return db_activity

def update_activity(db: Session, activity_id: str, activity_update: ActivityUpdate) -> Optional[Activity]:
    """Update an existing activity"""
    db_activity = get_activity_by_id(db, activity_id)
    if not db_activity:
        return None
    
    update_data = activity_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_activity, field, value)
    
    db.commit()
    db.refresh(db_activity)
    return db_activity

def delete_activity(db: Session, activity_id: str) -> bool:
    """Delete an activity (will also remove all offering associations due to CASCADE)"""
    db_activity = get_activity_by_id(db, activity_id)
    if not db_activity:
        return False
    
    db.delete(db_activity)
    db.commit()
    return True

def link_activity_to_offering(
    db: Session, 
    offering_activity: OfferingActivityCreate
) -> OfferingActivity:
    """Create a relationship between an offering and an activity"""
    db_link = OfferingActivity(**offering_activity.dict())
    db.add(db_link)
    db.commit()
    db.refresh(db_link)
    return db_link

def unlink_activity_from_offering(
    db: Session,
    offering_id: str,
    activity_id: str
) -> bool:
    """Remove relationship between offering and activity"""
    result = db.query(OfferingActivity).filter(
        and_(
            OfferingActivity.offering_id == offering_id,
            OfferingActivity.activity_id == activity_id
        )
    ).delete()
    db.commit()
    return result > 0

def update_activity_sequence(
    db: Session,
    offering_id: str,
    activity_id: str,
    sequence: int,
    is_mandatory: Optional[bool] = None
) -> Optional[OfferingActivity]:
    """Update sequence and mandatory flag for an activity in a specific offering"""
    db_link = db.query(OfferingActivity).filter(
        and_(
            OfferingActivity.offering_id == offering_id,
            OfferingActivity.activity_id == activity_id
        )
    ).first()
    
    if not db_link:
        return None
    
    db_link.sequence = sequence
    if is_mandatory is not None:
        db_link.is_mandatory = is_mandatory
    
    db.commit()
    db.refresh(db_link)
    return db_link

def get_offerings_for_activity(db: Session, activity_id: str) -> List[dict]:
    """Get all offerings that use a specific activity"""
    from app.models.offering import Offering
    
    results = db.query(Offering, OfferingActivity).join(
        OfferingActivity, Offering.offering_id == OfferingActivity.offering_id
    ).filter(
        OfferingActivity.activity_id == activity_id
    ).all()
    
    offerings = []
    for offering, offering_activity in results:
        offering_dict = {
            "offering_id": offering.offering_id,
            "offering_name": offering.offering_name,
            "sequence": offering_activity.sequence,
            "is_mandatory": offering_activity.is_mandatory
        }
        offerings.append(offering_dict)
    
    return offerings