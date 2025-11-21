from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.country import Country, CountryCreate, CountryUpdate
from app.crud import country as crud_country
from app.auth.dependencies import get_current_active_user
from app.auth.permissions import require_admin

router = APIRouter()

# READ - Available to all authenticated users
@router.get("/countries", response_model=List[Country])
async def get_countries(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Get list of all countries - Available to all authenticated users"""
    return crud_country.get_countries(db)

@router.get("/countries/{country_id}", response_model=Country)
async def get_country(
    country_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Get a specific country - Available to all authenticated users"""
    country = crud_country.get_country_by_id(db, country_id)
    if not country:
        raise HTTPException(status_code=404, detail="Country not found")
    return country

# WRITE - Administrator only
@router.post("/countries", response_model=Country, status_code=status.HTTP_201_CREATED)
async def create_country(
    country: CountryCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """Create a new country - **Requires Administrator access**"""
    return crud_country.create_country(db, country)

@router.put("/countries/{country_id}", response_model=Country)
async def update_country(
    country_id: str,
    country_update: CountryUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """Update a country - **Requires Administrator access**"""
    updated_country = crud_country.update_country(db, country_id, country_update)
    if not updated_country:
        raise HTTPException(status_code=404, detail="Country not found")
    return updated_country

@router.delete("/countries/{country_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_country(
    country_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """Delete a country - **Requires Administrator access**"""
    success = crud_country.delete_country(db, country_id)
    if not success:
        raise HTTPException(status_code=404, detail="Country not found")
    return None