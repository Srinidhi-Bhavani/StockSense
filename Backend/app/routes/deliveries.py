from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.delivery import (
    DeliveryCreate,
    DeliveryResponse,
    DeliveryItemCreate,
    DeliveryItemResponse
)
from app.services.delivery_service import (
    create_delivery,
    get_deliveries,
    get_delivery,
    get_delivery_items,
    add_delivery_item,
    delete_delivery_item,
    pick_delivery,
    pack_delivery,
    validate_delivery,
    cancel_delivery
)

router = APIRouter(
    prefix="/deliveries",
    tags=["Deliveries"]
)


@router.post("", response_model=DeliveryResponse, status_code=status.HTTP_201_CREATED)
def create_delivery_route(data: DeliveryCreate, db: Session = Depends(get_db)):
    return create_delivery(db, data)


@router.get("", response_model=List[DeliveryResponse])
def get_deliveries_route(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status: Optional[str] = None,
    warehouse_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    return get_deliveries(db, skip=skip, limit=limit, status=status, warehouse_id=warehouse_id)


@router.get("/{delivery_id}", response_model=DeliveryResponse)
def get_delivery_route(delivery_id: int, db: Session = Depends(get_db)):
    return get_delivery(db, delivery_id)


@router.get("/{delivery_id}/items", response_model=List[DeliveryItemResponse])
def get_delivery_items_route(delivery_id: int, db: Session = Depends(get_db)):
    return get_delivery_items(db, delivery_id)


@router.post("/{delivery_id}/items", response_model=DeliveryItemResponse, status_code=status.HTTP_201_CREATED)
def add_delivery_item_route(delivery_id: int, data: DeliveryItemCreate, db: Session = Depends(get_db)):
    return add_delivery_item(db, delivery_id, data)


@router.delete("/{delivery_id}/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_delivery_item_route(delivery_id: int, item_id: int, db: Session = Depends(get_db)):
    delete_delivery_item(db, delivery_id, item_id)


@router.post("/{delivery_id}/pick", response_model=DeliveryResponse)
def pick_delivery_route(delivery_id: int, db: Session = Depends(get_db)):
    return pick_delivery(db, delivery_id)


@router.post("/{delivery_id}/pack", response_model=DeliveryResponse)
def pack_delivery_route(delivery_id: int, db: Session = Depends(get_db)):
    return pack_delivery(db, delivery_id)


@router.post("/{delivery_id}/validate", response_model=DeliveryResponse)
def validate_delivery_route(delivery_id: int, db: Session = Depends(get_db)):
    return validate_delivery(db, delivery_id)


@router.post("/{delivery_id}/cancel", response_model=DeliveryResponse)
def cancel_delivery_route(delivery_id: int, db: Session = Depends(get_db)):
    return cancel_delivery(db, delivery_id)
