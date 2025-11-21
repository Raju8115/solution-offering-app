from sqlalchemy.orm import Session
from app.models.pricing import PricingDetail
from app.schemas.pricing import PricingDetailCreate, PricingDetailUpdate
from typing import Optional, List


def get_pricing_details(
    db: Session,
    country: str,
    role: str,
    band: int
) -> Optional[PricingDetail]:
    """Get pricing details for a specific country, role, and band"""
    return db.query(PricingDetail).filter(
        PricingDetail.country == country,
        PricingDetail.role == role,
        PricingDetail.band == band
    ).first()


def search_pricing(
    db: Session,
    country: Optional[str] = None,
    role: Optional[str] = None,
    band: Optional[int] = None
) -> List[PricingDetail]:
    """Search pricing details with optional filters"""
    query = db.query(PricingDetail)
    
    if country:
        query = query.filter(PricingDetail.country == country)
    if role:
        query = query.filter(PricingDetail.role == role)
    if band:
        query = query.filter(PricingDetail.band == band)
    
    return query.all()


def get_all_pricing(db: Session) -> List[PricingDetail]:
    """Get all pricing details"""
    return db.query(PricingDetail).all()


def create_pricing(db: Session, pricing: PricingDetailCreate) -> PricingDetail:
    """Create a new pricing detail"""
    db_pricing = PricingDetail(
        country=pricing.country,
        role=pricing.role,
        band=pricing.band,
        cost=pricing.cost,
        sale_price=pricing.sale_price
    )
    db.add(db_pricing)
    db.commit()
    db.refresh(db_pricing)
    return db_pricing


def update_pricing(
    db: Session,
    country: str,
    role: str,
    band: int,
    pricing: PricingDetailUpdate
) -> Optional[PricingDetail]:
    """Update an existing pricing detail"""
    db_pricing = db.query(PricingDetail).filter(
        PricingDetail.country == country,
        PricingDetail.role == role,
        PricingDetail.band == band
    ).first()
    
    if not db_pricing:
        return None
    
    update_data = pricing.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_pricing, field, value)
    
    db.commit()
    db.refresh(db_pricing)
    return db_pricing


def delete_pricing(
    db: Session,
    country: str,
    role: str,
    band: int
) -> bool:
    """Delete a pricing detail"""
    db_pricing = db.query(PricingDetail).filter(
        PricingDetail.country == country,
        PricingDetail.role == role,
        PricingDetail.band == band
    ).first()
    
    if not db_pricing:
        return False
    
    db.delete(db_pricing)
    db.commit()
    return True