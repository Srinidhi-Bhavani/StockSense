"""
Router: /api/v1/products
Full CRUD + search/filter endpoints for Products.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func

import crud.product as product_crud
import crud.category as cat_crud
import crud.uom as uom_crud
import crud.stock as stock_crud
from database.session import get_db
from models.product import Product
from schemas.product import (
    ProductCreate,
    ProductDetailResponse,
    ProductListResponse,
    ProductResponse,
    ProductUpdate,
    ReorderPointUpdate,
    StockStatus,
    StockSummary,
)

router = APIRouter(prefix="/products", tags=["Products"])


@router.get(
    "/",
    response_model=ProductListResponse,
    summary="List products with search and filters",
)
def list_products(
    search: str | None = Query(None, description="Search by product name or SKU"),
    category_id: int | None = Query(None, description="Filter by category ID"),
    uom_id: int | None = Query(None, description="Filter by Unit of Measure ID"),
    location_id: int | None = Query(None, description="Filter by warehouse/location ID"),
    stock_status: StockStatus | None = Query(None, description="Filter by stock status"),
    active_only: bool = Query(True, description="Show only active products"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
) -> ProductListResponse:
    items, total = product_crud.get_products(
        db,
        search=search,
        category_id=category_id,
        uom_id=uom_id,
        location_id=location_id,
        stock_status=stock_status,
        active_only=active_only,
        skip=skip,
        limit=limit,
    )
    return ProductListResponse(total=total, skip=skip, limit=limit, items=items)


@router.get(
    "/reorder-alerts",
    response_model=list[dict],
    summary="Products that have hit or breached their reorder point",
)
def reorder_alerts(db: Session = Depends(get_db)) -> list[dict]:
    """
    Returns all active products whose total stock is at or below their reorder_point.
    Useful for the dashboard to flag items that need purchasing.
    """
    return product_crud.get_products_needing_reorder(db)


@router.get(
    "/{product_id}",
    response_model=ProductDetailResponse,
    summary="Get a single product with stock information",
)
def get_product(
    product_id: int,
    location_id: int | None = Query(None, description="Optional location ID to scope stock summary"),
    db: Session = Depends(get_db),
) -> ProductDetailResponse:
    product = product_crud.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    stock_summary = product_crud.build_stock_summary(db, product, location_id=location_id)
    return ProductDetailResponse(
        **ProductResponse.model_validate(product).model_dump(),
        stock_summary=stock_summary,
    )


@router.get(
    "/{product_id}/stock-status",
    response_model=StockSummary,
    summary="Get stock status and total stock for a product",
)
def get_product_stock_status(
    product_id: int,
    location_id: int | None = Query(None, description="Optional location ID"),
    db: Session = Depends(get_db),
) -> StockSummary:
    product = product_crud.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product_crud.build_stock_summary(db, product, location_id=location_id)


@router.post(
    "/",
    response_model=ProductDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new product",
)
def create_product(data: ProductCreate, db: Session = Depends(get_db)) -> ProductDetailResponse:
    # 1. Validate Category existence
    if data.category_id is not None:
        cat = cat_crud.get_category(db, data.category_id)
        if not cat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with ID {data.category_id} not found",
            )

    # 2. Validate UOM existence
    uom = uom_crud.get_uom(db, data.uom_id)
    if not uom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Unit of Measure with ID {data.uom_id} not found",
        )

    # 3. Validate initial_location_id existence if provided
    if data.initial_location_id is not None:
        loc = stock_crud.get_location(db, data.initial_location_id)
        if not loc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Location with ID {data.initial_location_id} not found",
            )

    # 4. Check SKU uniqueness (case-insensitive)
    existing = (
        db.query(Product)
        .filter(func.lower(Product.sku) == data.sku.strip().lower())
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A product with SKU '{data.sku}' already exists",
        )

    product = product_crud.create_product(db, data)
    stock_summary = product_crud.build_stock_summary(db, product)
    return ProductDetailResponse(
        **ProductResponse.model_validate(product).model_dump(),
        stock_summary=stock_summary,
    )


@router.put(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Update a product",
)
def update_product(
    product_id: int, data: ProductUpdate, db: Session = Depends(get_db)
) -> ProductResponse:
    product = product_crud.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    # Validate category reference if updating
    if data.category_id is not None:
        cat = cat_crud.get_category(db, data.category_id)
        if not cat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with ID {data.category_id} not found",
            )

    # Validate uom reference if updating
    if data.uom_id is not None:
        uom = uom_crud.get_uom(db, data.uom_id)
        if not uom:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Unit of Measure with ID {data.uom_id} not found",
            )

    # Check SKU uniqueness if SKU is being changed
    if data.sku:
        conflict = (
            db.query(Product)
            .filter(func.lower(Product.sku) == data.sku.strip().lower(), Product.id != product_id)
            .first()
        )
        if conflict:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"SKU '{data.sku}' is already used by another product",
            )

    updated = product_crud.update_product(db, product_id, data)
    return updated


@router.patch(
    "/{product_id}/reorder-point",
    response_model=ProductResponse,
    summary="Configure minimum/reorder stock level for a product",
)
def set_reorder_point(
    product_id: int, data: ReorderPointUpdate, db: Session = Depends(get_db)
) -> ProductResponse:
    product = product_crud.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    updated = product_crud.update_product(
        db, product_id, ProductUpdate(reorder_point=data.reorder_point)
    )
    return updated


@router.delete(
    "/{product_id}",
    summary="Soft-delete a product (sets is_active=False)",
)
def delete_product(product_id: int, db: Session = Depends(get_db)) -> dict:
    success, message = product_crud.delete_product(db, product_id)
    if not success:
        code = (
            status.HTTP_404_NOT_FOUND
            if "not found" in message
            else status.HTTP_409_CONFLICT
        )
        raise HTTPException(status_code=code, detail=message)
    return {"detail": message}

