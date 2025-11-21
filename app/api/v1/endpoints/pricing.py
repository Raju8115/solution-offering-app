from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from sqlalchemy.orm import Session
from typing import Dict, List, Optional
from decimal import Decimal
from app.database import get_db
from app.schemas.pricing import PricingDetail, PricingDetailCreate, PricingDetailUpdate
from app.crud import pricing as crud_pricing
from app.crud import staffing as crud_staffing
from app.auth.dependencies import get_current_active_user
from app.auth.permissions import require_admin

router = APIRouter()

# READ - Available to all authenticated users

@router.get("/pricing/all", response_model=List[PricingDetail])
async def get_all_pricing(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Get all pricing details
    Available to all authenticated users
    """
    pricing_list = crud_pricing.get_all_pricing(db)
    return pricing_list


@router.get("/pricing/search", response_model=List[PricingDetail])
async def search_pricing(
    country: Optional[str] = Query(None, description="Country"),
    role: Optional[str] = Query(None, description="Role"),
    band: Optional[int] = Query(None, description="Band"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Search pricing details by country, role, and/or band
    Available to all authenticated users
    """
    pricing_list = crud_pricing.search_pricing(db, country=country, role=role, band=band)
    return pricing_list


@router.get("/pricingDetails", response_model=PricingDetail)
async def get_pricing_detail(
    country: str = Query(..., description="Country"),
    role: str = Query(..., description="Role"),
    band: int = Query(..., description="Band"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Get specific pricing details by country, role, and band
    Available to all authenticated users
    """
    pricing = crud_pricing.get_pricing_details(
        db=db,
        country=country,
        role=role,
        band=band
    )
    
    if not pricing:
        raise HTTPException(status_code=404, detail="Pricing details not found")
    
    return pricing


@router.get("/totalHoursAndPrices/{offering_id}")
async def get_total_hours_and_prices(
    offering_id: str = Path(..., description="Offering ID"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Calculate total hours and prices for an offering
    Available to all authenticated users
    """
    
    staffing_details = crud_staffing.get_staffing_by_offering(db, offering_id)
    
    if not staffing_details:
        return {
            "offering_id": offering_id,
            "total_hours": 0,
            "total_cost": 0,
            "total_sale_price": 0,
            "breakdown": []
        }
    
    total_hours = 0
    total_cost = Decimal(0)
    total_sale_price = Decimal(0)
    breakdown = []
    
    for staffing in staffing_details:
        pricing = crud_pricing.get_pricing_details(
            db=db,
            country=staffing.country,
            role=staffing.role,
            band=staffing.band
        )
        
        hours = staffing.hours or 0
        total_hours += hours
        
        if pricing:
            cost = (pricing.cost or Decimal(0)) * Decimal(hours)
            sale_price = (pricing.sale_price or Decimal(0)) * Decimal(hours)
            total_cost += cost
            total_sale_price += sale_price
            
            breakdown.append({
                "staffing_id": staffing.staffing_id,
                "country": staffing.country,
                "role": staffing.role,
                "band": staffing.band,
                "hours": hours,
                "cost_per_hour": float(pricing.cost) if pricing.cost else 0,
                "sale_price_per_hour": float(pricing.sale_price) if pricing.sale_price else 0,
                "total_cost": float(cost),
                "total_sale_price": float(sale_price)
            })
    
    return {
        "offering_id": offering_id,
        "total_hours": total_hours,
        "total_cost": float(total_cost),
        "total_sale_price": float(total_sale_price),
        "breakdown": breakdown
    }

# WRITE - Administrator only

@router.post("/pricingDetails", response_model=PricingDetail, status_code=status.HTTP_201_CREATED)
async def create_pricing(
    pricing: PricingDetailCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """Create new pricing details - **Requires Administrator access**"""
    # Check if pricing already exists for this combination
    existing = crud_pricing.get_pricing_details(
        db=db,
        country=pricing.country,
        role=pricing.role,
        band=pricing.band
    )
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Pricing already exists for this country, role, and band combination"
        )
    
    return crud_pricing.create_pricing(db, pricing)


@router.put("/pricingDetails/{country}/{role}/{band}", response_model=PricingDetail)
async def update_pricing(
    country: str = Path(..., description="Country"),
    role: str = Path(..., description="Role"),
    band: int = Path(..., description="Band"),
    pricing_update: PricingDetailUpdate = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """Update pricing details - **Requires Administrator access**"""
    updated_pricing = crud_pricing.update_pricing(db, country, role, band, pricing_update)
    if not updated_pricing:
        raise HTTPException(status_code=404, detail="Pricing details not found")
    return updated_pricing


@router.delete("/pricingDetails/{country}/{role}/{band}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pricing(
    country: str = Path(..., description="Country"),
    role: str = Path(..., description="Role"),
    band: int = Path(..., description="Band"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """Delete pricing details - **Requires Administrator access**"""
    success = crud_pricing.delete_pricing(db, country, role, band)
    if not success:
        raise HTTPException(status_code=404, detail="Pricing details not found")
    return None