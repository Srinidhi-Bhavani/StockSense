from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class StockAdjustmentCreate(BaseModel):
    product_id: int
    location_id: int
    actual_quantity: float
    reason: str


class StockAdjustmentDetail(BaseModel):
    id: int
    product_id: int
    location_id: int
    quantity: float
    old_quantity: Optional[float] = 0.0
    difference: Optional[float] = 0.0
    reason: str
    adjusted_by: Optional[int] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
