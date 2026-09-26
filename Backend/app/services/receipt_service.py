from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.receipt import Receipt, ReceiptItem
from app.models.product import Product
from app.models.location import Location
from app.services.stock_service import increase_stock


def create_receipt(
    db: Session,
    supplier: str,
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
            detail="Receipt must contain at least one item"
        )

    receipt = Receipt(
        supplier=supplier,
        warehouse_id=warehouse_id,
        location_id=location_id,
        status="Draft"
    )

    db.add(receipt)
    db.flush()

    # Assign reference number if not set
    receipt.reference_no = f"REC-{receipt.id:04d}"

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

        receipt_item = ReceiptItem(
            receipt_id=receipt.id,
            product_id=item["product_id"],
            quantity=item["quantity"]
        )
        db.add(receipt_item)

    db.commit()
    db.refresh(receipt)
    return receipt


def validate_receipt(db: Session, receipt_id: int, user_id: Optional[int] = None):
    receipt = db.query(Receipt).filter(
        Receipt.id == receipt_id
    ).first()

    if not receipt:
        raise HTTPException(
            status_code=404,
            detail="Receipt not found"
        )

    if receipt.status == "Done":
        raise HTTPException(
            status_code=400,
            detail="Receipt already validated"
        )

    items = db.query(ReceiptItem).filter(
        ReceiptItem.receipt_id == receipt_id
    ).all()

    if not items:
        raise HTTPException(
            status_code=400,
            detail="Receipt has no items"
        )

    for item in items:
        increase_stock(
            db=db,
            product_id=item.product_id,
            location_id=receipt.location_id,
            quantity=item.quantity,
            operation_type="RECEIPT",
            reference_id=receipt.id,
            user_id=user_id
        )

    receipt.status = "Done"
    db.commit()
    db.refresh(receipt)
    return receipt


def get_receipts(db: Session, status: Optional[str] = None) -> List[Receipt]:
    query = db.query(Receipt)
    if status:
        query = query.filter(Receipt.status == status)
    return query.order_by(Receipt.created_at.desc()).all()


def get_receipt_by_id(db: Session, receipt_id: int) -> Receipt:
    receipt = db.query(Receipt).filter(Receipt.id == receipt_id).first()
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")
    return receipt