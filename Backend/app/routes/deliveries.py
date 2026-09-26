from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.delivery import DeliveryCreate, DeliveryResponse
from app.services.delivery_service import (
    create_delivery,
    validate_delivery,
    get_deliveries,
    get_delivery_by_id
)
from app.utils.auth import get_current_user


router = APIRouter(
    prefix="/deliveries",
    tags=["Deliveries"]
)


@router.post("/", response_model=DeliveryResponse)
def create_delivery_route(
    data: DeliveryCreate,
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

    delivery = create_delivery(
        db=db,
        customer_reference=data.customer_reference,
        warehouse_id=data.warehouse_id,
        location_id=data.location_id,
        items=items
    )

    return delivery


@router.get("/", response_model=List[DeliveryResponse])
def list_deliveries(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_deliveries(db, status=status)


@router.get("/{delivery_id}", response_model=DeliveryResponse)
def get_delivery(
    delivery_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_delivery_by_id(db, delivery_id=delivery_id)


@router.post("/{delivery_id}/validate", response_model=DeliveryResponse)
def validate_delivery_route(
    delivery_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    delivery = validate_delivery(
        db=db,
        delivery_id=delivery_id,
        user_id=current_user.id
    )

    return delivery
