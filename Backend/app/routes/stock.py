from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.stock import (
    StockResponse,
    StockAdjustmentRequest,
    StockAdjustmentResponse,
    StockMovementResponse,
    ReorderAlertResponse
)
from app.services.stock_service import (
    get_stock,
    get_all_stock,
    adjust_stock,
    get_stock_movements,
    get_reorder_alerts
)
from app.utils.auth import get_current_user


router = APIRouter(prefix="/stock", tags=["Stock"])


@router.get("/", response_model=List[StockResponse])
def list_stock(
    product_id: Optional[int] = None,
    location_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_all_stock(db, product_id=product_id, location_id=location_id)


@router.get("/movements", response_model=List[StockMovementResponse])
def list_movements(
    product_id: Optional[int] = None,
    location_id: Optional[int] = None,
    operation_type: Optional[str] = None,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_stock_movements(
        db=db,
        product_id=product_id,
        location_id=location_id,
        operation_type=operation_type,
        limit=limit,
        offset=offset
    )


@router.get("/reorder-alerts", response_model=List[ReorderAlertResponse])
def check_reorder_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_reorder_alerts(db)


@router.get("/{product_id}/{location_id}")
def check_stock(
    product_id: int,
    location_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    quantity = get_stock(
        db,
        product_id,
        location_id
    )

    return {
        "product_id": product_id,
        "location_id": location_id,
        "quantity": quantity
    }


@router.post("/adjust", response_model=StockAdjustmentResponse)
def adjust_stock_route(
    data: StockAdjustmentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    adjustment = adjust_stock(
        db=db,
        product_id=data.product_id,
        location_id=data.location_id,
        actual_quantity=data.actual_quantity,
        reason=data.reason,
        user_id=current_user.id
    )

    return adjustment