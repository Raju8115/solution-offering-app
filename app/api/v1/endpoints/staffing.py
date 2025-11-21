from fastapi import APIRouter, Depends, Path, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.staffing import StaffingDetail, StaffingDetailCreate, StaffingDetailUpdate
from app.crud import staffing as crud_staffing
from app.auth.dependencies import get_current_active_user
from app.auth.permissions import require_admin

router = APIRouter()

@router.get("/staffingDetails/all", response_model=List[StaffingDetail])
async def get_all_staffing_details(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Get all staffing details - Available to all authenticated users"""
    staffing_details = crud_staffing.get_all_staffing(db)
    return staffing_details

@router.get("/staffingDetails/activity/{activity_id}", response_model=List[StaffingDetail])
async def get_staffing_by_activity(
    activity_id: str = Path(..., description="Activity ID"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Get staffing details by activity ID - Available to all authenticated users"""
    staffing_details = crud_staffing.get_staffing_by_activity(db, activity_id)
    return staffing_details

# READ - Available to all authenticated users
@router.get("/staffingDetails/{offering_id}", response_model=List[StaffingDetail])
async def get_staffing_details(
    offering_id: str = Path(..., description="Offering ID"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Get staffing details by offering ID - Available to all authenticated users"""
    staffing_details = crud_staffing.get_staffing_by_offering(db, offering_id)
    return staffing_details

@router.get("/staffingDetails/detail/{staffing_id}", response_model=StaffingDetail)
async def get_staffing_detail(
    staffing_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Get a specific staffing detail - Available to all authenticated users"""
    staffing = crud_staffing.get_staffing_by_id(db, staffing_id)
    if not staffing:
        raise HTTPException(status_code=404, detail="Staffing detail not found")
    return staffing

# WRITE - Administrator only
@router.post("/staffingDetails", response_model=StaffingDetail, status_code=status.HTTP_201_CREATED)
async def create_staffing_detail(
    staffing: StaffingDetailCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """Create a new staffing detail - **Requires Administrator access**"""
    return crud_staffing.create_staffing_detail(db, staffing)

@router.put("/staffingDetails/{staffing_id}", response_model=StaffingDetail)
async def update_staffing_detail(
    staffing_id: str,
    staffing_update: StaffingDetailUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """Update a staffing detail - **Requires Administrator access**"""
    updated_staffing = crud_staffing.update_staffing_detail(db, staffing_id, staffing_update)
    if not updated_staffing:
        raise HTTPException(status_code=404, detail="Staffing detail not found")
    return updated_staffing

@router.delete("/staffingDetails/{staffing_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_staffing_detail(
    staffing_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """Delete a staffing detail - **Requires Administrator access**"""
    success = crud_staffing.delete_staffing_detail(db, staffing_id)
    if not success:
        raise HTTPException(status_code=404, detail="Staffing detail not found")
    return None