from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.schemas.activity import (
    Activity,
    ActivityCreate,
    ActivityUpdate,
    ActivityWithRelation,
    ActivityWithOfferings,
    OfferingActivityCreate,
    OfferingActivityUpdate
)
from app.crud import activity as crud_activity
from app.crud import offering as crud_offering
from app.auth.dependencies import get_current_active_user
from app.auth.permissions import require_admin, require_solution_architect

router = APIRouter()

# ==================== Activity Library Management ====================
# READ operations - Available to all authenticated users (catalog access)

@router.get("/library", response_model=List[Activity])
async def get_activity_library(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)  # All authenticated users
):
    """
    Get all activities in the library (not filtered by offering)
    This is the activity catalog that can be used across offerings
    """
    activities = crud_activity.get_all_activities(db, skip=skip, limit=limit)
    return activities

@router.get("/library/unassigned", response_model=List[Activity])
async def get_unassigned_activities(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)  # All authenticated users
):
    """Get activities that are not assigned to any offering"""
    activities = crud_activity.get_unassigned_activities(db)
    return activities

@router.get("/library/{activity_id}", response_model=ActivityWithOfferings)
async def get_activity_detail(
    activity_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)  # All authenticated users
):
    """Get a single activity with all offerings using it"""
    activity = crud_activity.get_activity_by_id(db, activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    # Get all offerings using this activity
    offerings = crud_activity.get_offerings_for_activity(db, activity_id)
    
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
        "offerings": offerings
    }
    
    return activity_dict

@router.get("/activities", response_model=List[ActivityWithRelation])
async def get_activities_for_offering(
    offering_id: str = Query(..., description="Offering ID to get activities for"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)  # All authenticated users
):
    """
    Get all activities for a specific offering
    Includes offering-specific fields like sequence and is_mandatory
    """
    # Verify offering exists
    offering = crud_offering.get_offering_by_id(db, offering_id)
    if not offering:
        raise HTTPException(status_code=404, detail="Offering not found")
    
    activities = crud_activity.get_activities_by_offering(db, offering_id)
    return activities

# ==================== ADMIN ONLY - Modify Activity Library ====================

@router.post("/library", response_model=Activity, status_code=status.HTTP_201_CREATED)
async def create_activity(
    activity: ActivityCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)  # ADMIN ONLY
):
    """
    Create a new activity in the library (not associated with any offering yet)
    This activity can later be linked to one or more offerings
    **Requires Administrator access**
    """
    new_activity = crud_activity.create_activity(db, activity)
    return new_activity

@router.put("/library/{activity_id}", response_model=Activity)
async def update_activity(
    activity_id: str,
    activity_update: ActivityUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)  # ADMIN ONLY
):
    """
    Update an existing activity
    **Requires Administrator access**
    """
    updated_activity = crud_activity.update_activity(db, activity_id, activity_update)
    if not updated_activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    return updated_activity

@router.delete("/library/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_activity(
    activity_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)  # ADMIN ONLY
):
    """
    Delete an activity from the library
    This will also remove it from all offerings (CASCADE)
    **Requires Administrator access**
    """
    success = crud_activity.delete_activity(db, activity_id)
    if not success:
        raise HTTPException(status_code=404, detail="Activity not found")
    return None

# ==================== SOLUTION ARCHITECT - Link/Unlink Activities ====================

@router.post("/link", status_code=status.HTTP_201_CREATED)
async def link_activity_to_offering(
    link_data: OfferingActivityCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_solution_architect)  # SOLUTION ARCHITECT
):
    """
    Link an existing activity to an offering
    Allows reusing activities across multiple offerings
    **Requires Solution Architect access**
    """
    # Verify offering exists
    offering = crud_offering.get_offering_by_id(db, link_data.offering_id)
    if not offering:
        raise HTTPException(status_code=404, detail="Offering not found")
    
    # Verify activity exists
    activity = crud_activity.get_activity_by_id(db, link_data.activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    # Check if already linked
    existing_activities = crud_activity.get_activities_by_offering(db, link_data.offering_id)
    if any(a['activity_id'] == link_data.activity_id for a in existing_activities):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Activity already linked to this offering"
        )
    
    link = crud_activity.link_activity_to_offering(db, link_data)
    return {
        "message": "Activity linked to offering successfully",
        "offering_id": link.offering_id,
        "activity_id": link.activity_id,
        "sequence": link.sequence,
        "is_mandatory": link.is_mandatory
    }

@router.delete("/unlink")
async def unlink_activity_from_offering(
    offering_id: str = Query(..., description="Offering ID"),
    activity_id: str = Query(..., description="Activity ID"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_solution_architect)  # SOLUTION ARCHITECT
):
    """
    Remove an activity from an offering (doesn't delete the activity itself)
    **Requires Solution Architect access**
    """
    success = crud_activity.unlink_activity_from_offering(db, offering_id, activity_id)
    if not success:
        raise HTTPException(
            status_code=404,
            detail="Activity-Offering link not found"
        )
    return {"message": "Activity unlinked from offering successfully"}

@router.patch("/update-sequence")
async def update_activity_sequence_in_offering(
    offering_id: str = Query(..., description="Offering ID"),
    activity_id: str = Query(..., description="Activity ID"),
    update_data: OfferingActivityUpdate = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_solution_architect)  # SOLUTION ARCHITECT
):
    """
    Update sequence and mandatory flag for an activity in a specific offering
    **Requires Solution Architect access**
    """
    updated_link = crud_activity.update_activity_sequence(
        db,
        offering_id,
        activity_id,
        update_data.sequence if update_data and update_data.sequence is not None else None,
        update_data.is_mandatory if update_data else None
    )
    
    if not updated_link:
        raise HTTPException(
            status_code=404,
            detail="Activity-Offering link not found"
        )
    
    return {
        "message": "Activity sequence updated successfully",
        "offering_id": updated_link.offering_id,
        "activity_id": updated_link.activity_id,
        "sequence": updated_link.sequence,
        "is_mandatory": updated_link.is_mandatory
    }