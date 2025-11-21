from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.brand import Brand, BrandCreate, BrandUpdate
from app.crud import brand as crud_brand
from app.auth.dependencies import get_current_active_user
from app.auth.permissions import require_admin

router = APIRouter()

# READ - Available to all authenticated users
@router.get("/brands", response_model=List[Brand])
async def get_brands(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Get list of all brands - Available to all authenticated users"""
    return crud_brand.get_brands(db)

@router.get("/brands/{brand_id}", response_model=Brand)
async def get_brand(
    brand_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Get a specific brand - Available to all authenticated users"""
    brand = crud_brand.get_brand_by_id(db, brand_id)
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    return brand

# WRITE - Administrator only
@router.post("/brands", response_model=Brand, status_code=status.HTTP_201_CREATED)
async def create_brand(
    brand: BrandCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """Create a new brand - **Requires Administrator access**"""
    return crud_brand.create_brand(db, brand)

@router.put("/brands/{brand_id}", response_model=Brand)
async def update_brand(
    brand_id: str,
    brand_update: BrandUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """Update a brand - **Requires Administrator access**"""
    updated_brand = crud_brand.update_brand(db, brand_id, brand_update)
    if not updated_brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    return updated_brand

@router.delete("/brands/{brand_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_brand(
    brand_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """Delete a brand - **Requires Administrator access**"""
    success = crud_brand.delete_brand(db, brand_id)
    if not success:
        raise HTTPException(status_code=404, detail="Brand not found")
    return None