from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class TransferItemCreate(BaseModel):
    product_id: int
    quantity: float


class TransferItemResponse(BaseModel):
    id: int
    transfer_id: int
    product_id: int
    quantity: float

    class Config:
        from_attributes = True


class TransferCreate(BaseModel):
    warehouse_id: int
    source_location_id: int
    destination_location_id: int
    items: List[TransferItemCreate]


class TransferResponse(BaseModel):
    id: int
    reference_no: Optional[str] = None
    warehouse_id: int
    source_location_id: int
    destination_location_id: int
    status: str
    created_at: Optional[datetime] = None
    items: Optional[List[TransferItemResponse]] = []

    class Config:
        from_attributes = True
