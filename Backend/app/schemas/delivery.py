from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class DeliveryItemCreate(BaseModel):
    product_id: int
    quantity: float


class DeliveryItemResponse(BaseModel):
    id: int
    delivery_id: int
    product_id: int
    quantity: float

    class Config:
        from_attributes = True


class DeliveryCreate(BaseModel):
    customer_reference: str
    warehouse_id: int
    location_id: int
    items: List[DeliveryItemCreate]


class DeliveryResponse(BaseModel):
    id: int
    reference_no: Optional[str] = None
    customer_reference: str
    warehouse_id: int
    location_id: int
    status: str
    created_at: Optional[datetime] = None
    items: Optional[List[DeliveryItemResponse]] = []

    class Config:
        from_attributes = True
