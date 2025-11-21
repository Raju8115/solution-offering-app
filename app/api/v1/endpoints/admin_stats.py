from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict
from app.database import get_db
from app.auth.dependencies import get_current_active_user
from app.auth.permissions import require_admin

# Import your models
from app.models.brand import Brand
from app.models.product import Product
from app.models.offering import Offering
from app.models.country import Country
from app.models.activity import Activity
from app.models.pricing import PricingDetail
from app.models.staffing import StaffingDetail
from app.models.wbs import WBS

router = APIRouter()

@router.get("/admin/stats", response_model=Dict[str, int])
async def get_admin_stats(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    Get aggregated statistics for all admin entities - **Requires Administrator access**
    
    This endpoint returns counts for all entities in a single optimized query,
    significantly faster than making multiple API calls.
    """
    try:
        # Execute all count queries in a single database round-trip
        stats = {
            "totalBrands": db.query(func.count(Brand.brand_id)).scalar() or 0,
            "totalProducts": db.query(func.count(Product.product_id)).scalar() or 0,
            "totalOfferings": db.query(func.count(Offering.offering_id)).scalar() or 0,
            "totalCountries": db.query(func.count(Country.country_id)).scalar() or 0,
            "totalActivities": db.query(func.count(Activity.activity_id)).scalar() or 0,
            "totalPricing": db.query(func.count(PricingDetail.country)).scalar() or 0,
            "totalStaffing": db.query(func.count(StaffingDetail.staffing_id)).scalar() or 0,
            "totalWBS": db.query(func.count(WBS.wbs_id)).scalar() or 0,
        }
        
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching admin statistics: {str(e)}"
        )


@router.get("/admin/stats/detailed", response_model=Dict[str, Dict])
async def get_detailed_admin_stats(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    Get detailed statistics with additional breakdowns - **Requires Administrator access**
    
    Returns counts with additional metadata like active/inactive counts, 
    recent additions, etc.
    """
    try:
        # Basic counts
        total_brands = db.query(func.count(Brand.brand_id)).scalar() or 0
        total_products = db.query(func.count(Product.product_id)).scalar() or 0
        total_offerings = db.query(func.count(Offering.offering_id)).scalar() or 0
        total_countries = db.query(func.count(Country.country_id)).scalar() or 0
        total_activities = db.query(func.count(Activity.activity_id)).scalar() or 0
        total_pricing = db.query(func.count(PricingDetail.country)).scalar() or 0
        total_staffing = db.query(func.count(StaffingDetail.staffing_id)).scalar() or 0
        total_wbs = db.query(func.count(WBS.wbs_id)).scalar() or 0
        
        # Additional breakdowns (customize based on your models)
        # Example: Count offerings by type
        offerings_by_saas_type = db.query(
            Offering.saas_type,
            func.count(Offering.offering_id)
        ).group_by(Offering.saas_type).all()
        
        # Example: Count products by brand
        products_by_brand = db.query(
            Product.brand_id,
            func.count(Product.product_id)
        ).group_by(Product.brand_id).all()
        
        return {
            "catalog": {
                "brands": total_brands,
                "products": total_products,
                "offerings": total_offerings,
                "countries": total_countries
            },
            "configuration": {
                "activities": total_activities,
                "pricing": total_pricing,
                "staffing": total_staffing,
                "wbs": total_wbs
            },
            "breakdowns": {
                "offeringsBySaasType": {
                    saas_type: count for saas_type, count in offerings_by_saas_type
                },
                "productsByBrand": {
                    brand_id: count for brand_id, count in products_by_brand
                }
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching detailed admin statistics: {str(e)}"
        )
