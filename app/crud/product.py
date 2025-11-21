from sqlalchemy.orm import Session
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate
from typing import List, Optional
import uuid


def get_all_products(db: Session) -> List[Product]:
    """Get all products"""
    return db.query(Product).all()


def get_products_by_brand(db: Session, brand_id: str) -> List[Product]:
    """Get all products for a specific brand"""
    return db.query(Product).filter(Product.brand_id == brand_id).all()


def get_product_by_id(db: Session, product_id: str) -> Optional[Product]:
    """Get a single product by ID"""
    return db.query(Product).filter(Product.product_id == product_id).first()


def get_all_products(db: Session) -> List[Product]:
    """Get all products"""
    return db.query(Product).all()


def create_product(db: Session, product: ProductCreate) -> Product:
    """Create a new product"""
    db_product = Product(
        product_id=uuid.uuid4(),
        product_name=product.product_name,
        description=product.description,
        brand_id=product.brand_id
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def update_product(db: Session, product_id: str, product: ProductUpdate) -> Optional[Product]:
    """Update an existing product"""
    db_product = db.query(Product).filter(Product.product_id == product_id).first()
    
    if not db_product:
        return None
    
    update_data = product.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_product, field, value)
    
    db.commit()
    db.refresh(db_product)
    return db_product


def delete_product(db: Session, product_id: str) -> bool:
    """Delete a product"""
    db_product = db.query(Product).filter(Product.product_id == product_id).first()
    
    if not db_product:
        return False
    
    db.delete(db_product)
    db.commit()
    return True