from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database import get_db
from app.schemas.wbs import WBSCreate, WBSUpdate, WBSResponse, ActivityWBSCreate
from app.crud import wbs as crud_wbs
from app.auth.dependencies import get_current_active_user
from app.auth.permissions import require_admin

router = APIRouter(prefix="/wbs", tags=["WBS"])

# READ operations - Available to all authenticated users
@router.get("/", response_model=List[WBSResponse])
def get_all_wbs(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Get all WBS items (catalog access)"""
    return crud_wbs.get_all_wbs(db, skip, limit)

@router.get("/{wbs_id}", response_model=WBSResponse)
def get_wbs(
    wbs_id: UUID, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Get a specific WBS item (catalog access)"""
    db_wbs = crud_wbs.get_wbs(db, wbs_id)
    if not db_wbs:
        raise HTTPException(status_code=404, detail="WBS not found")
    return db_wbs

@router.get("/activity/{activity_id}/wbs", response_model=List[WBSResponse])
def get_wbs_for_activity(
    activity_id: UUID, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Get all WBS items for an activity (catalog access)"""
    return crud_wbs.get_wbs_for_activity(db, activity_id)

# WRITE operations - ADMIN ONLY
@router.post("/", response_model=WBSResponse)
def create_wbs(
    wbs: WBSCreate, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """Create a new WBS item - **Requires Administrator access**"""
    return crud_wbs.create_wbs(db, wbs)

@router.put("/{wbs_id}", response_model=WBSResponse)
def update_wbs(
    wbs_id: UUID, 
    wbs: WBSUpdate, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """Update a WBS item - **Requires Administrator access**"""
    db_wbs = crud_wbs.update_wbs(db, wbs_id, wbs)
    if not db_wbs:
        raise HTTPException(status_code=404, detail="WBS not found")
    return db_wbs

@router.delete("/{wbs_id}")
def delete_wbs(
    wbs_id: UUID, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """Delete a WBS item - **Requires Administrator access**"""
    if not crud_wbs.delete_wbs(db, wbs_id):
        raise HTTPException(status_code=404, detail="WBS not found")
    return {"message": "WBS deleted successfully"}

@router.post("/activity/{activity_id}/wbs/{wbs_id}")
def add_wbs_to_activity(
    activity_id: UUID, 
    wbs_id: UUID, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """Add WBS to activity - **Requires Administrator access**"""
    try:
        crud_wbs.add_wbs_to_activity(db, activity_id, wbs_id)
        return {"message": "WBS added to activity successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/activity/{activity_id}/wbs/{wbs_id}")
def remove_wbs_from_activity(
    activity_id: UUID, 
    wbs_id: UUID, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """Remove WBS from activity - **Requires Administrator access**"""
    if not crud_wbs.remove_wbs_from_activity(db, activity_id, wbs_id):
        raise HTTPException(status_code=404, detail="Association not found")
    return {"message": "WBS removed from activity successfully"}