from datetime import datetime
from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.delivery import Delivery, DeliveryItem
from app.models.stock import Stock
from app.models.stock_movement import StockMovement
from app.models.product import Product
from app.models.location import Location
from app.models.warehouse import Warehouse
from app.schemas.delivery import DeliveryCreate, DeliveryItemCreate


def create_delivery(db: Session, data: DeliveryCreate) -> Delivery:
    warehouse = db.query(Warehouse).filter(Warehouse.id == data.warehouse_id).first()
    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")

    location = db.query(Location).filter(Location.id == data.location_id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")

    if location.warehouse_id != data.warehouse_id:
        raise HTTPException(
            status_code=400,
            detail="Location does not belong to the selected warehouse"
        )

    delivery = Delivery(
        customer_reference=data.customer_reference,
        warehouse_id=data.warehouse_id,
        location_id=data.location_id,
        status="Draft"
    )
    db.add(delivery)
    db.flush()

    if data.items:
        for item in data.items:
            if item.quantity <= 0:
                raise HTTPException(
                    status_code=400,
                    detail="Quantity must be greater than zero"
                )

            product = db.query(Product).filter(Product.id == item.product_id).first()
            if not product:
                raise HTTPException(
                    status_code=404,
                    detail=f"Product {item.product_id} not found"
                )

            delivery_item = DeliveryItem(
                delivery_id=delivery.id,
                product_id=item.product_id,
                quantity=item.quantity
            )
            db.add(delivery_item)

    db.commit()
    db.refresh(delivery)
    return delivery


def get_deliveries(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    warehouse_id: Optional[int] = None
) -> List[Delivery]:
    query = db.query(Delivery)
    if status:
        query = query.filter(Delivery.status == status)
    if warehouse_id:
        query = query.filter(Delivery.warehouse_id == warehouse_id)
    return query.order_by(Delivery.id.desc()).offset(skip).limit(limit).all()


def get_delivery(db: Session, delivery_id: int) -> Delivery:
    delivery = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")
    return delivery


def get_delivery_items(db: Session, delivery_id: int) -> List[DeliveryItem]:
    get_delivery(db, delivery_id)
    return db.query(DeliveryItem).filter(DeliveryItem.delivery_id == delivery_id).all()


def add_delivery_item(db: Session, delivery_id: int, item_data: DeliveryItemCreate) -> DeliveryItem:
    delivery = get_delivery(db, delivery_id)
    if delivery.status != "Draft":
        raise HTTPException(
            status_code=400,
            detail="Can only add items to a Draft delivery"
        )

    if item_data.quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Quantity must be greater than zero"
        )

    product = db.query(Product).filter(Product.id == item_data.product_id).first()
    if not product:
        raise HTTPException(
            status_code=404,
            detail=f"Product {item_data.product_id} not found"
        )

    delivery_item = DeliveryItem(
        delivery_id=delivery.id,
        product_id=item_data.product_id,
        quantity=item_data.quantity
    )
    db.add(delivery_item)
    db.commit()
    db.refresh(delivery_item)
    return delivery_item


def delete_delivery_item(db: Session, delivery_id: int, item_id: int):
    delivery = get_delivery(db, delivery_id)
    if delivery.status != "Draft":
        raise HTTPException(
            status_code=400,
            detail="Can only remove items from a Draft delivery"
        )

    item = db.query(DeliveryItem).filter(
        DeliveryItem.id == item_id,
        DeliveryItem.delivery_id == delivery_id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Delivery item not found")

    db.delete(item)
    db.commit()


def pick_delivery(db: Session, delivery_id: int) -> Delivery:
    delivery = get_delivery(db, delivery_id)

    if delivery.status != "Draft":
        raise HTTPException(
            status_code=400,
            detail="Only Draft deliveries can be picked"
        )

    delivery.status = "Waiting"
    db.commit()
    db.refresh(delivery)
    return delivery


def pack_delivery(db: Session, delivery_id: int) -> Delivery:
    delivery = get_delivery(db, delivery_id)

    if delivery.status != "Waiting":
        raise HTTPException(
            status_code=400,
            detail="Delivery must be picked before packing"
        )

    delivery.status = "Ready"
    db.commit()
    db.refresh(delivery)
    return delivery


def validate_delivery(db: Session, delivery_id: int) -> Delivery:
    delivery = get_delivery(db, delivery_id)

    if delivery.status == "Done":
        raise HTTPException(status_code=400, detail="Delivery already validated")
    if delivery.status == "Canceled":
        raise HTTPException(status_code=400, detail="Canceled delivery cannot be validated")

    if delivery.status != "Ready":
        raise HTTPException(
            status_code=400,
            detail="Delivery must be packed before validation"
        )

    items = db.query(DeliveryItem).filter(DeliveryItem.delivery_id == delivery.id).all()
    if not items:
        raise HTTPException(status_code=400, detail="Delivery has no items")

    # Check all stock before updating anything to avoid partial updates
    for item in items:
        stock = db.query(Stock).filter(
            Stock.product_id == item.product_id,
            Stock.warehouse_id == delivery.warehouse_id,
            Stock.location_id == delivery.location_id
        ).first()

        if not stock:
            raise HTTPException(
                status_code=400,
                detail=f"No stock found for product {item.product_id}"
            )

        if stock.quantity < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for product {item.product_id}"
            )

    # Deduct stock and record stock movements
    for item in items:
        stock = db.query(Stock).filter(
            Stock.product_id == item.product_id,
            Stock.warehouse_id == delivery.warehouse_id,
            Stock.location_id == delivery.location_id
        ).first()

        stock.quantity -= item.quantity

        movement = StockMovement(
            product_id=item.product_id,
            warehouse_id=delivery.warehouse_id,
            source_location_id=delivery.location_id,
            destination_location_id=None,
            movement_type="DELIVERY",
            quantity=item.quantity,
            reference_id=delivery.id
        )
        db.add(movement)

    delivery.status = "Done"
    db.commit()
    db.refresh(delivery)
    return delivery


def cancel_delivery(db: Session, delivery_id: int) -> Delivery:
    delivery = get_delivery(db, delivery_id)
    if delivery.status == "Done":
        raise HTTPException(status_code=400, detail="Cannot cancel a completed delivery")
    if delivery.status == "Canceled":
        raise HTTPException(status_code=400, detail="Delivery is already canceled")

    delivery.status = "Canceled"
    db.commit()
    db.refresh(delivery)
    return delivery
