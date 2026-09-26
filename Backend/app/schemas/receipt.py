from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class ReceiptItemCreate(BaseModel):
    product_id: int
    quantity: float = Field(gt=0, description="Quantity must be greater than zero")


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
    items: List[ReceiptItemCreate] = []


class ReceiptResponse(BaseModel):
    id: int
    supplier: str
    warehouse_id: int
    location_id: int
    status: str
    created_at: Optional[datetime] = None
    items: List[ReceiptItemResponse] = []

    class Config:
        from_attributes = True
