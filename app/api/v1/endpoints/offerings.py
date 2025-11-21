from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.schemas.offering import Offering, OfferingCreate, OfferingUpdate
from app.crud import offering as crud_offering
from app.auth.dependencies import get_current_active_user
from app.auth.permissions import require_admin

router = APIRouter()

# READ - Available to all authenticated users
@router.get("/offerings", response_model=List[Offering])
async def get_offerings(
    product_id: str = Query(..., description="Product ID to filter offerings"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Get offerings by product ID - Available to all authenticated users"""
    offerings = crud_offering.get_offerings_by_product(db, product_id)
    return offerings

@router.get("/offerings/{offering_id}", response_model=Offering)
async def get_offering_by_id(
    offering_id: str = Path(..., description="Offering ID"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Get offering by offering ID - Available to all authenticated users"""
    offering = crud_offering.get_offering_by_id(db, offering_id)
    if not offering:
        raise HTTPException(status_code=404, detail="Offering not found")
    return offering

@router.get("/offerings/search/", response_model=List[Offering])
async def search_offerings(
    query: Optional[str] = Query(None, description="Search query"),
    saas_type: Optional[str] = Query(None, description="Filter by SaaS type"),
    industry: Optional[str] = Query(None, description="Filter by industry"),
    client_type: Optional[str] = Query(None, description="Filter by client type"),
    framework_category: Optional[str] = Query(None, description="Filter by framework category"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Search offerings with multiple filters - Available to all authenticated users"""
    offerings = crud_offering.search_offerings(
        db=db,
        query=query,
        saas_type=saas_type,
        industry=industry,
        client_type=client_type,
        framework_category=framework_category
    )
    return offerings

# WRITE - Administrator only
@router.post("/offerings", response_model=Offering, status_code=status.HTTP_201_CREATED)
async def create_offering(
    offering: OfferingCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """Create a new offering - **Requires Administrator access**"""
    return crud_offering.create_offering(db, offering)

@router.put("/offerings/{offering_id}", response_model=Offering)
async def update_offering(
    offering_id: str,
    offering_update: OfferingUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """Update an offering - **Requires Administrator access**"""
    updated_offering = crud_offering.update_offering(db, offering_id, offering_update)
    if not updated_offering:
        raise HTTPException(status_code=404, detail="Offering not found")
    return updated_offering

@router.delete("/offerings/{offering_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_offering(
    offering_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """Delete an offering - **Requires Administrator access**"""
    success = crud_offering.delete_offering(db, offering_id)
    if not success:
        raise HTTPException(status_code=404, detail="Offering not found")
    return None