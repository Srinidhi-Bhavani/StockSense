from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class ReceiptItemCreate(BaseModel):
    product_id: int
    quantity: float


class ReceiptItemResponse(BaseModel):
    id: int
    receipt_id: int
    product_id: int
    quantity: float

    class Config:
        from_attributes = True


class ReceiptCreate(BaseModel):
    supplier: str
    warehouse_id: int
    location_id: int
    items: List[ReceiptItemCreate]


class ReceiptResponse(BaseModel):
    id: int
    reference_no: Optional[str] = None
    supplier: str
    warehouse_id: int
    location_id: int
    status: str
    created_at: Optional[datetime] = None
    items: Optional[List[ReceiptItemResponse]] = []

    class Config:
        from_attributes = True