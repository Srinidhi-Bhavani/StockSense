from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.delivery import Delivery, DeliveryItem
from app.models.product import Product
from app.models.location import Location
from app.services.stock_service import decrease_stock, get_stock


def create_delivery(
    db: Session,
    customer_reference: str,
    warehouse_id: int,
    location_id: int,
    items: list
):
    location = db.query(Location).filter(
        Location.id == location_id,
        Location.warehouse_id == warehouse_id
    ).first()

    if not location:
        raise HTTPException(
            status_code=404,
            detail="Location not found in this warehouse"
        )

    if not items:
        raise HTTPException(
            status_code=400,
            detail="Delivery must contain at least one item"
        )

    delivery = Delivery(
        customer_reference=customer_reference,
        warehouse_id=warehouse_id,
        location_id=location_id,
        status="Draft"
    )

    db.add(delivery)
    db.flush()

    delivery.reference_no = f"DEL-{delivery.id:04d}"

    for item in items:
        product = db.query(Product).filter(
            Product.id == item["product_id"],
            Product.is_active == True
        ).first()

        if not product:
            raise HTTPException(
                status_code=404,
                detail=f"Product {item['product_id']} not found or inactive"
            )

        if item["quantity"] <= 0:
            raise HTTPException(
                status_code=400,
                detail="Quantity must be greater than zero"
            )

        delivery_item = DeliveryItem(
            delivery_id=delivery.id,
            product_id=item["product_id"],
            quantity=item["quantity"]
        )
        db.add(delivery_item)

    db.commit()
    db.refresh(delivery)
    return delivery


def validate_delivery(db: Session, delivery_id: int, user_id: Optional[int] = None):
    delivery = db.query(Delivery).filter(
        Delivery.id == delivery_id
    ).first()

    if not delivery:
        raise HTTPException(
            status_code=404,
            detail="Delivery not found"
        )

    if delivery.status == "Done":
        raise HTTPException(
            status_code=400,
            detail="Delivery already validated"
        )

    items = db.query(DeliveryItem).filter(
        DeliveryItem.delivery_id == delivery_id
    ).all()

    if not items:
        raise HTTPException(
            status_code=400,
            detail="Delivery has no items"
        )

    # 1. Pre-check stock availability for all items before applying any changes
    for item in items:
        current_qty = get_stock(db, item.product_id, delivery.location_id)
        if current_qty < item.quantity:
            prod = db.query(Product).filter(Product.id == item.product_id).first()
            prod_name = prod.name if prod else f"ID {item.product_id}"
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for '{prod_name}'. On hand: {current_qty}, Requested: {item.quantity}"
            )

    # 2. Deduct stock and record movements
    for item in items:
        decrease_stock(
            db=db,
            product_id=item.product_id,
            location_id=delivery.location_id,
            quantity=item.quantity,
            operation_type="DELIVERY",
            reference_id=delivery.id,
            user_id=user_id
        )

    delivery.status = "Done"
    db.commit()
    db.refresh(delivery)
    return delivery


def get_deliveries(db: Session, status: Optional[str] = None) -> List[Delivery]:
    query = db.query(Delivery)
    if status:
        query = query.filter(Delivery.status == status)
    return query.order_by(Delivery.created_at.desc()).all()


def get_delivery_by_id(db: Session, delivery_id: int) -> Delivery:
    delivery = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")
    return delivery
