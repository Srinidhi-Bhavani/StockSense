from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class DeliveryItemCreate(BaseModel):
    product_id: int
    quantity: float = Field(gt=0, description="Quantity must be greater than zero")


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
    items: List[DeliveryItemCreate] = []


class DeliveryResponse(BaseModel):
    id: int
    customer_reference: str
    warehouse_id: int
    location_id: int
    status: str
    created_at: Optional[datetime] = None
    items: List[DeliveryItemResponse] = []

    class Config:
        from_attributes = True
