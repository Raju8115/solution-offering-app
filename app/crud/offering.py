from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.offering import Offering
from app.schemas.offering import OfferingCreate, OfferingUpdate
from datetime import datetime
import uuid


def get_offerings_by_product(db: Session, product_id: str) -> List[Offering]:
    """Get all offerings for a specific product"""
    return db.query(Offering).filter(Offering.product_id == product_id).all()


def get_offering_by_id(db: Session, offering_id: str) -> Optional[Offering]:
    """Get a single offering by ID"""
    return db.query(Offering).filter(Offering.offering_id == offering_id).first()


def search_offerings(
    db: Session,
    query: Optional[str] = None,
    saas_type: Optional[str] = None,
    industry: Optional[str] = None,
    client_type: Optional[str] = None,
    framework_category: Optional[str] = None
) -> List[Offering]:
    """Search offerings with multiple filters"""
    db_query = db.query(Offering)
    
    if query:
        db_query = db_query.filter(
            (Offering.offering_name.ilike(f"%{query}%")) |
            (Offering.offering_summary.ilike(f"%{query}%")) |
            (Offering.tag_line.ilike(f"%{query}%"))
        )
    
    if saas_type:
        db_query = db_query.filter(Offering.saas_type == saas_type)
    
    if industry:
        db_query = db_query.filter(Offering.industry == industry)
    
    if client_type:
        db_query = db_query.filter(Offering.client_type == client_type)
    
    if framework_category:
        db_query = db_query.filter(Offering.framework_category == framework_category)
    
    return db_query.all()


# ✅ ADD THESE NEW FUNCTIONS

def create_offering(db: Session, offering: OfferingCreate) -> Offering:
    """Create a new offering"""
    db_offering = Offering(
        offering_id=uuid.uuid4(),
        offering_name=offering.offering_name,
        product_id=offering.product_id,
        saas_type=offering.saas_type,
        brand=offering.brand,
        supported_product=offering.supported_product,
        client_type=offering.client_type,
        client_journey=offering.client_journey,
        client_journey_stage=offering.client_journey_stage,
        framework_category=offering.framework_category,
        scenario=offering.scenario,
        ibm_sales_play=offering.ibm_sales_play,
        tel_sales_tactic=offering.tel_sales_tactic,
        industry=offering.industry,
        offering_tags=offering.offering_tags,
        content_page=offering.content_page,
        offering_sales_contact=offering.offering_sales_contact,
        offering_product_manager=offering.offering_product_manager,
        offering_practice_leader=offering.offering_practice_leader,
        business_challenges=offering.business_challenges,
        business_drivers=offering.business_drivers,
        offering_value=offering.offering_value,
        tag_line=offering.tag_line,
        elevator_pitch=offering.elevator_pitch,
        offering_outcomes=offering.offering_outcomes,
        key_deliverables=offering.key_deliverables,
        offering_summary=offering.offering_summary,
        when_and_why_to_sell=offering.when_and_why_to_sell,
        buyer_persona=offering.buyer_persona,
        user_persona=offering.user_persona,
        scope_summary=offering.scope_summary,
        duration=offering.duration,
        occ=offering.occ,
        prerequisites=offering.prerequisites,
        seismic_link=offering.seismic_link,
        part_numbers=offering.part_numbers,
        created_on=datetime.utcnow(),
        updated_on=datetime.utcnow()
    )
    
    db.add(db_offering)
    db.commit()
    db.refresh(db_offering)
    return db_offering


def update_offering(db: Session, offering_id: str, offering: OfferingUpdate) -> Optional[Offering]:
    """Update an existing offering"""
    db_offering = db.query(Offering).filter(Offering.offering_id == offering_id).first()
    
    if not db_offering:
        return None
    
    # Update only the fields that are provided (not None)
    update_data = offering.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_offering, field, value)
    
    db_offering.updated_on = datetime.utcnow()
    
    db.commit()
    db.refresh(db_offering)
    return db_offering


def delete_offering(db: Session, offering_id: str) -> bool:
    """Delete an offering"""
    db_offering = db.query(Offering).filter(Offering.offering_id == offering_id).first()
    
    if not db_offering:
        return False
    
    db.delete(db_offering)
    db.commit()
    return True