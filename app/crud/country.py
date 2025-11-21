from sqlalchemy.orm import Session
from app.models.country import Country
from app.schemas.country import CountryCreate, CountryUpdate
from typing import List, Optional
import uuid


def get_countries(db: Session) -> List[Country]:
    """Get all countries"""
    return db.query(Country).all()


def get_country_by_id(db: Session, country_id: str) -> Optional[Country]:
    """Get a single country by ID"""
    return db.query(Country).filter(Country.country_id == country_id).first()


def create_country(db: Session, country: CountryCreate) -> Country:
    """Create a new country"""
    db_country = Country(
        country_id=uuid.uuid4(),
        country_name=country.country_name
    )
    db.add(db_country)
    db.commit()
    db.refresh(db_country)
    return db_country


def update_country(db: Session, country_id: str, country: CountryUpdate) -> Optional[Country]:
    """Update an existing country"""
    db_country = db.query(Country).filter(Country.country_id == country_id).first()
    
    if not db_country:
        return None
    
    update_data = country.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_country, field, value)
    
    db.commit()
    db.refresh(db_country)
    return db_country


def delete_country(db: Session, country_id: str) -> bool:
    """Delete a country"""
    db_country = db.query(Country).filter(Country.country_id == country_id).first()
    
    if not db_country:
        return False
    
    db.delete(db_country)
    db.commit()
    return True