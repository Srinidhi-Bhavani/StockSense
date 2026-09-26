from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.receipt import ReceiptCreate, ReceiptResponse
from app.services.receipt_service import (
    create_receipt,
    validate_receipt,
    get_receipts,
    get_receipt_by_id
)
from app.utils.auth import get_current_user


router = APIRouter(
    prefix="/receipts",
    tags=["Receipts"]
)


@router.post("/", response_model=ReceiptResponse)
def create_receipt_route(
    data: ReceiptCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    items = [
        {
            "product_id": item.product_id,
            "quantity": item.quantity
        }
        for item in data.items
    ]

    receipt = create_receipt(
        db=db,
        supplier=data.supplier,
        warehouse_id=data.warehouse_id,
        location_id=data.location_id,
        items=items
    )

    return receipt


@router.get("/", response_model=List[ReceiptResponse])
def list_receipts(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_receipts(db, status=status)


@router.get("/{receipt_id}", response_model=ReceiptResponse)
def get_receipt(
    receipt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_receipt_by_id(db, receipt_id=receipt_id)


@router.post("/{receipt_id}/validate", response_model=ReceiptResponse)
def validate_receipt_route(
    receipt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    receipt = validate_receipt(
        db=db,
        receipt_id=receipt_id,
        user_id=current_user.id
    )

    return receipt