from typing import Optional, List
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.stock import Stock
from app.models.stock_movement import StockMovement
from app.models.adjustment import StockAdjustment
from app.models.reorder_rule import ReorderRule
from app.models.product import Product
from app.models.location import Location


def get_stock(
    db: Session,
    product_id: int,
    location_id: int
) -> float:
    stock = db.query(Stock).filter(
        Stock.product_id == product_id,
        Stock.location_id == location_id
    ).first()

    if not stock:
        return 0.0

    return stock.quantity


def get_all_stock(
    db: Session,
    product_id: Optional[int] = None,
    location_id: Optional[int] = None
) -> List[Stock]:
    query = db.query(Stock)
    if product_id:
        query = query.filter(Stock.product_id == product_id)
    if location_id:
        query = query.filter(Stock.location_id == location_id)
    return query.all()


def increase_stock(
    db: Session,
    product_id: int,
    location_id: int,
    quantity: float,
    operation_type: str,
    reference_id: Optional[int] = None,
    user_id: Optional[int] = None
):
    if quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Quantity must be greater than zero"
        )

    stock = db.query(Stock).filter(
        Stock.product_id == product_id,
        Stock.location_id == location_id
    ).first()

    if not stock:
        stock = Stock(
            product_id=product_id,
            location_id=location_id,
            quantity=0.0
        )
        db.add(stock)
        db.flush()

    stock.quantity += quantity

    movement = StockMovement(
        product_id=product_id,
        quantity=quantity,
        destination_location_id=location_id,
        operation_type=operation_type,
        reference_id=reference_id,
        user_id=user_id
    )

    db.add(movement)
    return stock


def decrease_stock(
    db: Session,
    product_id: int,
    location_id: int,
    quantity: float,
    operation_type: str,
    reference_id: Optional[int] = None,
    user_id: Optional[int] = None
):
    if quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Quantity must be greater than zero"
        )

    stock = db.query(Stock).filter(
        Stock.product_id == product_id,
        Stock.location_id == location_id
    ).first()

    if not stock or stock.quantity < quantity:
        available = stock.quantity if stock else 0.0
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient stock for product {product_id} at location {location_id}. Available: {available}, Required: {quantity}"
        )

    stock.quantity -= quantity

    movement = StockMovement(
        product_id=product_id,
        quantity=quantity,
        source_location_id=location_id,
        operation_type=operation_type,
        reference_id=reference_id,
        user_id=user_id
    )

    db.add(movement)
    return stock


def adjust_stock(
    db: Session,
    product_id: int,
    location_id: int,
    actual_quantity: float,
    reason: str,
    user_id: Optional[int] = None
):
    if actual_quantity < 0:
        raise HTTPException(
            status_code=400,
            detail="Actual quantity cannot be negative"
        )

    # Verify product and location exist
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")

    stock = db.query(Stock).filter(
        Stock.product_id == product_id,
        Stock.location_id == location_id
    ).first()

    if not stock:
        stock = Stock(
            product_id=product_id,
            location_id=location_id,
            quantity=0.0
        )
        db.add(stock)
        db.flush()

    old_quantity = stock.quantity
    difference = actual_quantity - old_quantity

    stock.quantity = actual_quantity

    # 1. Record in stock_adjustments table
    adjustment = StockAdjustment(
        product_id=product_id,
        location_id=location_id,
        quantity=actual_quantity,
        old_quantity=old_quantity,
        difference=difference,
        reason=reason,
        adjusted_by=user_id
    )
    db.add(adjustment)
    db.flush()

    # 2. Record in immutable stock_movements ledger if there is a difference
    if abs(difference) > 0:
        movement = StockMovement(
            product_id=product_id,
            quantity=abs(difference),
            source_location_id=location_id if difference < 0 else None,
            destination_location_id=location_id if difference > 0 else None,
            operation_type="ADJUSTMENT",
            reference_id=adjustment.id,
            user_id=user_id
        )
        db.add(movement)

    db.commit()
    db.refresh(stock)
    db.refresh(adjustment)

    return adjustment


def get_stock_movements(
    db: Session,
    product_id: Optional[int] = None,
    location_id: Optional[int] = None,
    operation_type: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
) -> List[StockMovement]:
    query = db.query(StockMovement)

    if product_id:
        query = query.filter(StockMovement.product_id == product_id)
    if location_id:
        query = query.filter(
            (StockMovement.source_location_id == location_id) |
            (StockMovement.destination_location_id == location_id)
        )
    if operation_type:
        query = query.filter(StockMovement.operation_type == operation_type.upper())

    return query.order_by(StockMovement.created_at.desc()).offset(offset).limit(limit).all()


def get_reorder_alerts(db: Session):
    rules = db.query(ReorderRule).all()
    alerts = []

    for rule in rules:
        current_qty = get_stock(db, rule.product_id, rule.location_id)
        if current_qty <= rule.reorder_level:
            prod = db.query(Product).filter(Product.id == rule.product_id).first()
            loc = db.query(Location).filter(Location.id == rule.location_id).first()

            alerts.append({
                "product_id": rule.product_id,
                "product_name": prod.name if prod else "Unknown",
                "sku": prod.sku if prod else "Unknown",
                "location_id": rule.location_id,
                "location_name": loc.name if loc else "Unknown",
                "current_stock": current_qty,
                "reorder_level": rule.reorder_level,
                "reorder_quantity": rule.reorder_quantity
            })

    return alerts