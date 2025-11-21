from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.product import Product, ProductCreate, ProductUpdate
from app.crud import product as crud_product
from app.auth.dependencies import get_current_active_user
from app.auth.permissions import require_admin

router = APIRouter()

# READ - Available to all authenticated users
@router.get("/products/all", response_model=List[Product])
async def get_all_products(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Get all products - Available to all authenticated users"""
    products = crud_product.get_all_products(db)
    return products

@router.get("/products", response_model=List[Product])
async def get_products(
    brand_id: str = Query(..., description="Brand ID to filter products"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Get products by brand ID - Available to all authenticated users"""
    products = crud_product.get_products_by_brand(db, brand_id)
    return products

@router.get("/products/{product_id}", response_model=Product)
async def get_product(
    product_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Get a specific product - Available to all authenticated users"""
    product = crud_product.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

# WRITE - Administrator only
@router.post("/products", response_model=Product, status_code=status.HTTP_201_CREATED)
async def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """Create a new product - **Requires Administrator access**"""
    return crud_product.create_product(db, product)

@router.put("/products/{product_id}", response_model=Product)
async def update_product(
    product_id: str,
    product_update: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """Update a product - **Requires Administrator access**"""
    updated_product = crud_product.update_product(db, product_id, product_update)
    if not updated_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return updated_product

@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """Delete a product - **Requires Administrator access**"""
    success = crud_product.delete_product(db, product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Product not found")
    return None