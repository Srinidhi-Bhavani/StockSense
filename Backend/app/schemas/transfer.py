from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class TransferItemCreate(BaseModel):
    product_id: int
    quantity: float = Field(gt=0, description="Quantity must be greater than zero")


class TransferItemResponse(BaseModel):
    id: int
    transfer_id: int
    product_id: int
    quantity: float

    class Config:
        from_attributes = True


class TransferCreate(BaseModel):
    source_warehouse_id: int
    source_location_id: int
    destination_warehouse_id: int
    destination_location_id: int
    items: List[TransferItemCreate] = []


class TransferResponse(BaseModel):
    id: int
    source_warehouse_id: int
    source_location_id: int
    destination_warehouse_id: int
    destination_location_id: int
    status: str
    created_at: Optional[datetime] = None
    items: List[TransferItemResponse] = []

    class Config:
        from_attributes = True
