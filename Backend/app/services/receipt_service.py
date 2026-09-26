from datetime import datetime
from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.receipt import Receipt, ReceiptItem
from app.models.stock import Stock
from app.models.stock_movement import StockMovement
from app.models.product import Product
from app.models.location import Location
from app.models.warehouse import Warehouse
from app.schemas.receipt import ReceiptCreate, ReceiptItemCreate


def create_receipt(db: Session, data: ReceiptCreate) -> Receipt:
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

    receipt = Receipt(
        supplier=data.supplier,
        warehouse_id=data.warehouse_id,
        location_id=data.location_id,
        status="Draft"
    )
    db.add(receipt)
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

            receipt_item = ReceiptItem(
                receipt_id=receipt.id,
                product_id=item.product_id,
                quantity=item.quantity
            )
            db.add(receipt_item)

    db.commit()
    db.refresh(receipt)
    return receipt


def get_receipts(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    warehouse_id: Optional[int] = None
) -> List[Receipt]:
    query = db.query(Receipt)
    if status:
        query = query.filter(Receipt.status == status)
    if warehouse_id:
        query = query.filter(Receipt.warehouse_id == warehouse_id)
    return query.order_by(Receipt.id.desc()).offset(skip).limit(limit).all()


def get_receipt(db: Session, receipt_id: int) -> Receipt:
    receipt = db.query(Receipt).filter(Receipt.id == receipt_id).first()
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")
    return receipt


def get_receipt_items(db: Session, receipt_id: int) -> List[ReceiptItem]:
    get_receipt(db, receipt_id)
    return db.query(ReceiptItem).filter(ReceiptItem.receipt_id == receipt_id).all()


def add_receipt_item(db: Session, receipt_id: int, item_data: ReceiptItemCreate) -> ReceiptItem:
    receipt = get_receipt(db, receipt_id)
    if receipt.status != "Draft":
        raise HTTPException(
            status_code=400,
            detail="Can only add items to a Draft receipt"
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

    receipt_item = ReceiptItem(
        receipt_id=receipt.id,
        product_id=item_data.product_id,
        quantity=item_data.quantity
    )
    db.add(receipt_item)
    db.commit()
    db.refresh(receipt_item)
    return receipt_item


def delete_receipt_item(db: Session, receipt_id: int, item_id: int):
    receipt = get_receipt(db, receipt_id)
    if receipt.status != "Draft":
        raise HTTPException(
            status_code=400,
            detail="Can only remove items from a Draft receipt"
        )

    item = db.query(ReceiptItem).filter(
        ReceiptItem.id == item_id,
        ReceiptItem.receipt_id == receipt_id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Receipt item not found")

    db.delete(item)
    db.commit()


def validate_receipt(db: Session, receipt_id: int) -> Receipt:
    receipt = get_receipt(db, receipt_id)

    if receipt.status == "Done":
        raise HTTPException(status_code=400, detail="Receipt already validated")
    if receipt.status == "Canceled":
        raise HTTPException(status_code=400, detail="Canceled receipt cannot be validated")

    items = db.query(ReceiptItem).filter(ReceiptItem.receipt_id == receipt.id).all()
    if not items:
        raise HTTPException(status_code=400, detail="Receipt has no items")

    for item in items:
        stock = db.query(Stock).filter(
            Stock.product_id == item.product_id,
            Stock.warehouse_id == receipt.warehouse_id,
            Stock.location_id == receipt.location_id
        ).first()

        if stock:
            stock.quantity += item.quantity
        else:
            stock = Stock(
                product_id=item.product_id,
                warehouse_id=receipt.warehouse_id,
                location_id=receipt.location_id,
                quantity=item.quantity
            )
            db.add(stock)

        movement = StockMovement(
            product_id=item.product_id,
            warehouse_id=receipt.warehouse_id,
            source_location_id=None,
            destination_location_id=receipt.location_id,
            movement_type="RECEIPT",
            quantity=item.quantity,
            reference_id=receipt.id
        )
        db.add(movement)

    receipt.status = "Done"
    db.commit()
    db.refresh(receipt)
    return receipt


def cancel_receipt(db: Session, receipt_id: int) -> Receipt:
    receipt = get_receipt(db, receipt_id)
    if receipt.status == "Done":
        raise HTTPException(status_code=400, detail="Cannot cancel a completed receipt")
    if receipt.status == "Canceled":
        raise HTTPException(status_code=400, detail="Receipt is already canceled")

    receipt.status = "Canceled"
    db.commit()
    db.refresh(receipt)
    return receipt
