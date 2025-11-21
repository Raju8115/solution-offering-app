from sqlalchemy.orm import Session
from app.models.brand import Brand
from app.schemas.brand import BrandCreate, BrandUpdate
from typing import List, Optional
from datetime import datetime
import uuid


def get_brands(db: Session) -> List[Brand]:
    """Get all brands"""
    return db.query(Brand).all()


def get_brand_by_id(db: Session, brand_id: str) -> Optional[Brand]:
    """Get a single brand by ID"""
    return db.query(Brand).filter(Brand.brand_id == brand_id).first()


def create_brand(db: Session, brand: BrandCreate) -> Brand:
    """Create a new brand"""
    db_brand = Brand(
        brand_id=uuid.uuid4(),
        brand_name=brand.brand_name,
        description=brand.description
    )
    db.add(db_brand)
    db.commit()
    db.refresh(db_brand)
    return db_brand


def update_brand(db: Session, brand_id: str, brand: BrandUpdate) -> Optional[Brand]:
    """Update an existing brand"""
    db_brand = db.query(Brand).filter(Brand.brand_id == brand_id).first()
    
    if not db_brand:
        return None
    
    update_data = brand.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_brand, field, value)
    
    db.commit()
    db.refresh(db_brand)
    return db_brand


def delete_brand(db: Session, brand_id: str) -> bool:
    """Delete a brand"""
    db_brand = db.query(Brand).filter(Brand.brand_id == brand_id).first()
    
    if not db_brand:
        return False
    
    db.delete(db_brand)
    db.commit()
    return True