from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.receipt import (
    ReceiptCreate,
    ReceiptResponse,
    ReceiptItemCreate,
    ReceiptItemResponse
)
from app.services.receipt_service import (
    create_receipt,
    get_receipts,
    get_receipt,
    get_receipt_items,
    add_receipt_item,
    delete_receipt_item,
    validate_receipt,
    cancel_receipt
)

router = APIRouter(
    prefix="/receipts",
    tags=["Receipts"]
)


@router.post("", response_model=ReceiptResponse, status_code=status.HTTP_201_CREATED)
def create_receipt_route(data: ReceiptCreate, db: Session = Depends(get_db)):
    return create_receipt(db, data)


@router.get("", response_model=List[ReceiptResponse])
def get_receipts_route(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status: Optional[str] = None,
    warehouse_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    return get_receipts(db, skip=skip, limit=limit, status=status, warehouse_id=warehouse_id)


@router.get("/{receipt_id}", response_model=ReceiptResponse)
def get_receipt_route(receipt_id: int, db: Session = Depends(get_db)):
    return get_receipt(db, receipt_id)


@router.get("/{receipt_id}/items", response_model=List[ReceiptItemResponse])
def get_receipt_items_route(receipt_id: int, db: Session = Depends(get_db)):
    return get_receipt_items(db, receipt_id)


@router.post("/{receipt_id}/items", response_model=ReceiptItemResponse, status_code=status.HTTP_201_CREATED)
def add_receipt_item_route(receipt_id: int, data: ReceiptItemCreate, db: Session = Depends(get_db)):
    return add_receipt_item(db, receipt_id, data)


@router.delete("/{receipt_id}/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_receipt_item_route(receipt_id: int, item_id: int, db: Session = Depends(get_db)):
    delete_receipt_item(db, receipt_id, item_id)


@router.post("/{receipt_id}/validate", response_model=ReceiptResponse)
def validate_receipt_route(receipt_id: int, db: Session = Depends(get_db)):
    return validate_receipt(db, receipt_id)


@router.post("/{receipt_id}/cancel", response_model=ReceiptResponse)
def cancel_receipt_route(receipt_id: int, db: Session = Depends(get_db)):
    return cancel_receipt(db, receipt_id)
