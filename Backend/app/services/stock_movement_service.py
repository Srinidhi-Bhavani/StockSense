from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.stock_movement import StockMovement


def get_stock_movements(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    product_id: Optional[int] = None,
    warehouse_id: Optional[int] = None,
    movement_type: Optional[str] = None,
    reference_id: Optional[int] = None
) -> List[StockMovement]:
    query = db.query(StockMovement)
    if product_id:
        query = query.filter(StockMovement.product_id == product_id)
    if warehouse_id:
        query = query.filter(StockMovement.warehouse_id == warehouse_id)
    if movement_type:
        query = query.filter(StockMovement.movement_type == movement_type)
    if reference_id:
        query = query.filter(StockMovement.reference_id == reference_id)
    return query.order_by(StockMovement.id.desc()).offset(skip).limit(limit).all()


def get_stock_movement(db: Session, movement_id: int) -> StockMovement:
    movement = db.query(StockMovement).filter(StockMovement.id == movement_id).first()
    if not movement:
        raise HTTPException(status_code=404, detail="Stock movement not found")
    return movement
