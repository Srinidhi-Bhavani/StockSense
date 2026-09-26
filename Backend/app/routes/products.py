from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.product import Product
from app.models.category import Category
from app.models.user import User
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.utils.auth import get_current_user


router = APIRouter(prefix="/products", tags=["Products"])


@router.post("/", response_model=ProductResponse)
def create_product(
    data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    existing_product = db.query(Product).filter(
        Product.sku == data.sku
    ).first()

    if existing_product:
        raise HTTPException(
            status_code=400,
            detail="SKU already exists"
        )

    category_name = data.category
    category_id = data.category_id

    # Resolve category and category_id mutually
    if category_id:
        cat = db.query(Category).filter(Category.id == category_id).first()
        if not cat:
            raise HTTPException(status_code=404, detail="Category not found")
        if not category_name:
            category_name = cat.name
    elif category_name:
        cat = db.query(Category).filter(Category.name.ilike(category_name)).first()
        if cat:
            category_id = cat.id
        else:
            cat = Category(name=category_name)
            db.add(cat)
            db.flush()
            category_id = cat.id
    else:
        category_name = "General"

    product = Product(
        name=data.name,
        sku=data.sku,
        category=category_name,
        category_id=category_id,
        uom=data.uom,
        initial_stock=data.initial_stock,
        is_active=True
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    return product


@router.get("/", response_model=List[ProductResponse])
def get_products(
    category_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Product).filter(Product.is_active == True)
    if category_id:
        query = query.filter(Product.category_id == category_id)
    return query.order_by(Product.name).all()


@router.get("/search", response_model=List[ProductResponse])
def search_products(
    q: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Product).filter(
        Product.is_active == True,
        (
            Product.name.ilike(f"%{q}%") |
            Product.sku.ilike(f"%{q}%")
        )
    ).all()


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.is_active == True
    ).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return product


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if data.sku and data.sku != product.sku:
        existing_sku = db.query(Product).filter(Product.sku == data.sku).first()
        if existing_sku:
            raise HTTPException(status_code=400, detail="SKU already exists")
        product.sku = data.sku

    if data.name is not None:
        product.name = data.name
    if data.category is not None:
        product.category = data.category
    if data.category_id is not None:
        product.category_id = data.category_id
        cat = db.query(Category).filter(Category.id == data.category_id).first()
        if cat and not data.category:
            product.category = cat.name
    if data.uom is not None:
        product.uom = data.uom
    if data.initial_stock is not None:
        product.initial_stock = data.initial_stock
    if data.is_active is not None:
        product.is_active = data.is_active

    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    product.is_active = False
    db.commit()

    return {"message": "Product deactivated successfully", "product_id": product_id}