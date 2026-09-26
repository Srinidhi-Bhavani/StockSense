from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.transfer import InternalTransfer, TransferItem
from app.models.product import Product
from app.models.location import Location
from app.models.stock import Stock
from app.models.stock_movement import StockMovement
from app.services.stock_service import get_stock


def create_transfer(
    db: Session,
    warehouse_id: int,
    source_location_id: int,
    destination_location_id: int,
    items: list
):
    if source_location_id == destination_location_id:
        raise HTTPException(
            status_code=400,
            detail="Source and destination locations cannot be the same"
        )

    src_loc = db.query(Location).filter(
        Location.id == source_location_id,
        Location.warehouse_id == warehouse_id
    ).first()
    if not src_loc:
        raise HTTPException(status_code=404, detail="Source location not found in this warehouse")

    dst_loc = db.query(Location).filter(
        Location.id == destination_location_id,
        Location.warehouse_id == warehouse_id
    ).first()
    if not dst_loc:
        raise HTTPException(status_code=404, detail="Destination location not found in this warehouse")

    if not items:
        raise HTTPException(status_code=400, detail="Transfer must contain at least one item")

    transfer = InternalTransfer(
        warehouse_id=warehouse_id,
        source_location_id=source_location_id,
        destination_location_id=destination_location_id,
        status="Draft"
    )

    db.add(transfer)
    db.flush()

    transfer.reference_no = f"TRF-{transfer.id:04d}"

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

        transfer_item = TransferItem(
            transfer_id=transfer.id,
            product_id=item["product_id"],
            quantity=item["quantity"]
        )
        db.add(transfer_item)

    db.commit()
    db.refresh(transfer)
    return transfer


def validate_transfer(db: Session, transfer_id: int, user_id: Optional[int] = None):
    transfer = db.query(InternalTransfer).filter(
        InternalTransfer.id == transfer_id
    ).first()

    if not transfer:
        raise HTTPException(status_code=404, detail="Transfer not found")

    if transfer.status == "Done":
        raise HTTPException(status_code=400, detail="Transfer already validated")

    items = db.query(TransferItem).filter(
        TransferItem.transfer_id == transfer_id
    ).all()

    if not items:
        raise HTTPException(status_code=400, detail="Transfer has no items")

    # 1. Pre-check available stock at source location for all items
    for item in items:
        current_qty = get_stock(db, item.product_id, transfer.source_location_id)
        if current_qty < item.quantity:
            prod = db.query(Product).filter(Product.id == item.product_id).first()
            prod_name = prod.name if prod else f"ID {item.product_id}"
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for '{prod_name}' at source location. Available: {current_qty}, Required: {item.quantity}"
            )

    # 2. Perform two-legged relocation: deduct source, credit destination
    for item in items:
        # Deduct source
        source_stock = db.query(Stock).filter(
            Stock.product_id == item.product_id,
            Stock.location_id == transfer.source_location_id
        ).first()
        source_stock.quantity -= item.quantity

        # Credit destination
        dest_stock = db.query(Stock).filter(
            Stock.product_id == item.product_id,
            Stock.location_id == transfer.destination_location_id
        ).first()

        if not dest_stock:
            dest_stock = Stock(
                product_id=item.product_id,
                location_id=transfer.destination_location_id,
                quantity=0.0
            )
            db.add(dest_stock)
            db.flush()

        dest_stock.quantity += item.quantity

        # Record movement
        movement = StockMovement(
            product_id=item.product_id,
            quantity=item.quantity,
            source_location_id=transfer.source_location_id,
            destination_location_id=transfer.destination_location_id,
            operation_type="TRANSFER",
            reference_id=transfer.id,
            user_id=user_id
        )
        db.add(movement)

    transfer.status = "Done"
    db.commit()
    db.refresh(transfer)
    return transfer


def get_transfers(db: Session, status: Optional[str] = None) -> List[InternalTransfer]:
    query = db.query(InternalTransfer)
    if status:
        query = query.filter(InternalTransfer.status == status)
    return query.order_by(InternalTransfer.created_at.desc()).all()


def get_transfer_by_id(db: Session, transfer_id: int) -> InternalTransfer:
    transfer = db.query(InternalTransfer).filter(InternalTransfer.id == transfer_id).first()
    if not transfer:
        raise HTTPException(status_code=404, detail="Transfer not found")
    return transfer
