from datetime import datetime
from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.transfer import InternalTransfer, TransferItem
from app.models.stock import Stock
from app.models.stock_movement import StockMovement
from app.models.product import Product
from app.models.location import Location
from app.models.warehouse import Warehouse
from app.schemas.transfer import TransferCreate, TransferItemCreate


def create_transfer(db: Session, data: TransferCreate) -> InternalTransfer:
    if (
        data.source_warehouse_id == data.destination_warehouse_id
        and data.source_location_id == data.destination_location_id
    ):
        raise HTTPException(
            status_code=400,
            detail="Source and destination cannot be the same"
        )

    source_warehouse = db.query(Warehouse).filter(
        Warehouse.id == data.source_warehouse_id
    ).first()
    if not source_warehouse:
        raise HTTPException(status_code=404, detail="Source warehouse not found")

    destination_warehouse = db.query(Warehouse).filter(
        Warehouse.id == data.destination_warehouse_id
    ).first()
    if not destination_warehouse:
        raise HTTPException(status_code=404, detail="Destination warehouse not found")

    source_location = db.query(Location).filter(
        Location.id == data.source_location_id
    ).first()
    if not source_location:
        raise HTTPException(status_code=404, detail="Source location not found")

    destination_location = db.query(Location).filter(
        Location.id == data.destination_location_id
    ).first()
    if not destination_location:
        raise HTTPException(status_code=404, detail="Destination location not found")

    if source_location.warehouse_id != data.source_warehouse_id:
        raise HTTPException(
            status_code=400,
            detail="Source location does not belong to source warehouse"
        )

    if destination_location.warehouse_id != data.destination_warehouse_id:
        raise HTTPException(
            status_code=400,
            detail="Destination location does not belong to destination warehouse"
        )

    transfer = InternalTransfer(
        source_warehouse_id=data.source_warehouse_id,
        source_location_id=data.source_location_id,
        destination_warehouse_id=data.destination_warehouse_id,
        destination_location_id=data.destination_location_id,
        status="Draft"
    )
    db.add(transfer)
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

            transfer_item = TransferItem(
                transfer_id=transfer.id,
                product_id=item.product_id,
                quantity=item.quantity
            )
            db.add(transfer_item)

    db.commit()
    db.refresh(transfer)
    return transfer


def get_transfers(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    source_warehouse_id: Optional[int] = None,
    destination_warehouse_id: Optional[int] = None
) -> List[InternalTransfer]:
    query = db.query(InternalTransfer)
    if status:
        query = query.filter(InternalTransfer.status == status)
    if source_warehouse_id:
        query = query.filter(InternalTransfer.source_warehouse_id == source_warehouse_id)
    if destination_warehouse_id:
        query = query.filter(InternalTransfer.destination_warehouse_id == destination_warehouse_id)
    return query.order_by(InternalTransfer.id.desc()).offset(skip).limit(limit).all()


def get_transfer(db: Session, transfer_id: int) -> InternalTransfer:
    transfer = db.query(InternalTransfer).filter(InternalTransfer.id == transfer_id).first()
    if not transfer:
        raise HTTPException(status_code=404, detail="Transfer not found")
    return transfer


def get_transfer_items(db: Session, transfer_id: int) -> List[TransferItem]:
    get_transfer(db, transfer_id)
    return db.query(TransferItem).filter(TransferItem.transfer_id == transfer_id).all()


def add_transfer_item(db: Session, transfer_id: int, item_data: TransferItemCreate) -> TransferItem:
    transfer = get_transfer(db, transfer_id)
    if transfer.status != "Draft":
        raise HTTPException(
            status_code=400,
            detail="Can only add items to a Draft transfer"
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

    transfer_item = TransferItem(
        transfer_id=transfer.id,
        product_id=item_data.product_id,
        quantity=item_data.quantity
    )
    db.add(transfer_item)
    db.commit()
    db.refresh(transfer_item)
    return transfer_item


def delete_transfer_item(db: Session, transfer_id: int, item_id: int):
    transfer = get_transfer(db, transfer_id)
    if transfer.status != "Draft":
        raise HTTPException(
            status_code=400,
            detail="Can only remove items from a Draft transfer"
        )

    item = db.query(TransferItem).filter(
        TransferItem.id == item_id,
        TransferItem.transfer_id == transfer_id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Transfer item not found")

    db.delete(item)
    db.commit()


def validate_transfer(db: Session, transfer_id: int) -> InternalTransfer:
    transfer = get_transfer(db, transfer_id)

    if transfer.status == "Done":
        raise HTTPException(status_code=400, detail="Transfer already completed")
    if transfer.status == "Canceled":
        raise HTTPException(status_code=400, detail="Canceled transfer cannot be validated")

    items = db.query(TransferItem).filter(TransferItem.transfer_id == transfer.id).all()
    if not items:
        raise HTTPException(status_code=400, detail="Transfer has no items")

    # Check all source stock before changing anything
    for item in items:
        source_stock = db.query(Stock).filter(
            Stock.product_id == item.product_id,
            Stock.warehouse_id == transfer.source_warehouse_id,
            Stock.location_id == transfer.source_location_id
        ).first()

        if not source_stock:
            raise HTTPException(
                status_code=400,
                detail=f"No source stock for product {item.product_id}"
            )

        if source_stock.quantity < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for product {item.product_id}"
            )

    # Move stock from source to destination
    for item in items:
        source_stock = db.query(Stock).filter(
            Stock.product_id == item.product_id,
            Stock.warehouse_id == transfer.source_warehouse_id,
            Stock.location_id == transfer.source_location_id
        ).first()

        source_stock.quantity -= item.quantity

        destination_stock = db.query(Stock).filter(
            Stock.product_id == item.product_id,
            Stock.warehouse_id == transfer.destination_warehouse_id,
            Stock.location_id == transfer.destination_location_id
        ).first()

        if destination_stock:
            destination_stock.quantity += item.quantity
        else:
            destination_stock = Stock(
                product_id=item.product_id,
                warehouse_id=transfer.destination_warehouse_id,
                location_id=transfer.destination_location_id,
                quantity=item.quantity
            )
            db.add(destination_stock)

        movement = StockMovement(
            product_id=item.product_id,
            warehouse_id=transfer.source_warehouse_id,
            source_location_id=transfer.source_location_id,
            destination_location_id=transfer.destination_location_id,
            movement_type="INTERNAL_TRANSFER",
            quantity=item.quantity,
            reference_id=transfer.id
        )
        db.add(movement)

    transfer.status = "Done"
    db.commit()
    db.refresh(transfer)
    return transfer


def cancel_transfer(db: Session, transfer_id: int) -> InternalTransfer:
    transfer = get_transfer(db, transfer_id)
    if transfer.status == "Done":
        raise HTTPException(status_code=400, detail="Cannot cancel a completed transfer")
    if transfer.status == "Canceled":
        raise HTTPException(status_code=400, detail="Transfer is already canceled")

    transfer.status = "Canceled"
    db.commit()
    db.refresh(transfer)
    return transfer
