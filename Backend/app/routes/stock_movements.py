from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.stock_movement import StockMovementResponse
from app.services.stock_movement_service import (
    get_stock_movements,
    get_stock_movement
)

router = APIRouter(
    prefix="/stock-movements",
    tags=["Stock Movement History"]
)


@router.get("", response_model=List[StockMovementResponse])
def get_stock_movements_route(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    product_id: Optional[int] = None,
    warehouse_id: Optional[int] = None,
    movement_type: Optional[str] = None,
    reference_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    return get_stock_movements(
        db,
        skip=skip,
        limit=limit,
        product_id=product_id,
        warehouse_id=warehouse_id,
        movement_type=movement_type,
        reference_id=reference_id
    )


@router.get("/{movement_id}", response_model=StockMovementResponse)
def get_stock_movement_route(movement_id: int, db: Session = Depends(get_db)):
    return get_stock_movement(db, movement_id)
