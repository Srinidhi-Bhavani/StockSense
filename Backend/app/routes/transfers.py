from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.transfer import TransferCreate, TransferResponse
from app.services.transfer_service import (
    create_transfer,
    validate_transfer,
    get_transfers,
    get_transfer_by_id
)
from app.utils.auth import get_current_user


router = APIRouter(
    prefix="/transfers",
    tags=["Internal Transfers"]
)


@router.post("/", response_model=TransferResponse)
def create_transfer_route(
    data: TransferCreate,
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

    transfer = create_transfer(
        db=db,
        warehouse_id=data.warehouse_id,
        source_location_id=data.source_location_id,
        destination_location_id=data.destination_location_id,
        items=items
    )

    return transfer


@router.get("/", response_model=List[TransferResponse])
def list_transfers(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_transfers(db, status=status)


@router.get("/{transfer_id}", response_model=TransferResponse)
def get_transfer(
    transfer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_transfer_by_id(db, transfer_id=transfer_id)


@router.post("/{transfer_id}/validate", response_model=TransferResponse)
def validate_transfer_route(
    transfer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    transfer = validate_transfer(
        db=db,
        transfer_id=transfer_id,
        user_id=current_user.id
    )

    return transfer
