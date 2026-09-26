from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.transfer import (
    TransferCreate,
    TransferResponse,
    TransferItemCreate,
    TransferItemResponse
)
from app.services.transfer_service import (
    create_transfer,
    get_transfers,
    get_transfer,
    get_transfer_items,
    add_transfer_item,
    delete_transfer_item,
    validate_transfer,
    cancel_transfer
)

router = APIRouter(
    prefix="/transfers",
    tags=["Internal Transfers"]
)


@router.post("", response_model=TransferResponse, status_code=status.HTTP_201_CREATED)
def create_transfer_route(data: TransferCreate, db: Session = Depends(get_db)):
    return create_transfer(db, data)


@router.get("", response_model=List[TransferResponse])
def get_transfers_route(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status: Optional[str] = None,
    source_warehouse_id: Optional[int] = None,
    destination_warehouse_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    return get_transfers(
        db,
        skip=skip,
        limit=limit,
        status=status,
        source_warehouse_id=source_warehouse_id,
        destination_warehouse_id=destination_warehouse_id
    )


@router.get("/{transfer_id}", response_model=TransferResponse)
def get_transfer_route(transfer_id: int, db: Session = Depends(get_db)):
    return get_transfer(db, transfer_id)


@router.get("/{transfer_id}/items", response_model=List[TransferItemResponse])
def get_transfer_items_route(transfer_id: int, db: Session = Depends(get_db)):
    return get_transfer_items(db, transfer_id)


@router.post("/{transfer_id}/items", response_model=TransferItemResponse, status_code=status.HTTP_201_CREATED)
def add_transfer_item_route(transfer_id: int, data: TransferItemCreate, db: Session = Depends(get_db)):
    return add_transfer_item(db, transfer_id, data)


@router.delete("/{transfer_id}/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transfer_item_route(transfer_id: int, item_id: int, db: Session = Depends(get_db)):
    delete_transfer_item(db, transfer_id, item_id)


@router.post("/{transfer_id}/validate", response_model=TransferResponse)
def validate_transfer_route(transfer_id: int, db: Session = Depends(get_db)):
    return validate_transfer(db, transfer_id)


@router.post("/{transfer_id}/cancel", response_model=TransferResponse)
def cancel_transfer_route(transfer_id: int, db: Session = Depends(get_db)):
    return cancel_transfer(db, transfer_id)
