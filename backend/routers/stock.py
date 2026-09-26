"""
Router: /api/v1/stock
Endpoints for stock levels (by location) and warehouse locations.
Designed to be consumed by Receipts, Deliveries, and Internal Transfers modules.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import crud.product as product_crud
import crud.stock as stock_crud
from database.session import get_db
from schemas.stock import (
    InitialStockCreate,
    LocationCreate,
    LocationResponse,
    StockAdjust,
    StockLevelResponse,
)

router = APIRouter(prefix="/stock", tags=["Stock & Locations"])


# ---------------------------------------------------------------------------
# Locations
# ---------------------------------------------------------------------------

@router.get(
    "/locations",
    response_model=list[LocationResponse],
    summary="List all warehouse/store locations",
)
def list_locations(
    active_only: bool = True,
    db: Session = Depends(get_db),
) -> list[LocationResponse]:
    return stock_crud.get_locations(db, active_only=active_only)


@router.post(
    "/locations",
    response_model=LocationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new warehouse/store location",
)
def create_location(
    data: LocationCreate, db: Session = Depends(get_db)
) -> LocationResponse:
    return stock_crud.create_location(db, data)


@router.get(
    "/locations/{location_id}",
    response_model=LocationResponse,
    summary="Get a single location",
)
def get_location(location_id: int, db: Session = Depends(get_db)) -> LocationResponse:
    loc = stock_crud.get_location(db, location_id)
    if not loc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found")
    return loc


# ---------------------------------------------------------------------------
# Stock Levels
# ---------------------------------------------------------------------------

@router.get(
    "/product/{product_id}",
    response_model=list[StockLevelResponse],
    summary="Get stock levels for a product across all locations",
)
def get_stock_for_product(
    product_id: int, db: Session = Depends(get_db)
) -> list[StockLevelResponse]:
    product = product_crud.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return stock_crud.get_stock_for_product(db, product_id)


@router.get(
    "/location/{location_id}",
    response_model=list[StockLevelResponse],
    summary="Get stock levels for all products at a specific location",
)
def get_stock_for_location(
    location_id: int, db: Session = Depends(get_db)
) -> list[StockLevelResponse]:
    loc = stock_crud.get_location(db, location_id)
    if not loc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found")
    return stock_crud.get_stock_for_location(db, location_id)


@router.post(
    "/initial",
    response_model=StockLevelResponse,
    status_code=status.HTTP_200_OK,
    summary="Set initial (opening) stock for a product at a location",
)
def set_initial_stock(
    data: InitialStockCreate, db: Session = Depends(get_db)
) -> StockLevelResponse:
    """
    Sets (overwrites) the stock quantity for a product-location pair.
    Use this for opening balance / initial stock entry ONLY.
    For day-to-day movements, use /stock/adjust.
    """
    product = product_crud.get_product(db, data.product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {data.product_id} not found",
        )
    loc = stock_crud.get_location(db, data.location_id)
    if not loc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Location with ID {data.location_id} not found",
        )

    sl = stock_crud.set_initial_stock(db, data)
    return StockLevelResponse(
        id=sl.id,
        product_id=sl.product_id,
        location_id=sl.location_id,
        quantity=sl.quantity,
        updated_at=sl.updated_at,
        location_name=loc.name,
        location_code=loc.code,
    )


@router.post(
    "/adjust",
    response_model=StockLevelResponse,
    summary="Adjust stock by delta (used by Receipts / Deliveries / Transfers)",
)
def adjust_stock(
    data: StockAdjust, db: Session = Depends(get_db)
) -> StockLevelResponse:
    """
    Delta-based stock adjustment:
    - Positive delta → stock increases (Receipts)
    - Negative delta → stock decreases (Deliveries)
    - Call twice for Internal Transfers (subtract source, add destination)
    """
    product = product_crud.get_product(db, data.product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {data.product_id} not found",
        )
    loc = stock_crud.get_location(db, data.location_id)
    if not loc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Location with ID {data.location_id} not found",
        )

    sl = stock_crud.adjust_stock(db, data)
    return StockLevelResponse(
        id=sl.id,
        product_id=sl.product_id,
        location_id=sl.location_id,
        quantity=sl.quantity,
        updated_at=sl.updated_at,
        location_name=loc.name,
        location_code=loc.code,
    )

