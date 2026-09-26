from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ReorderRuleCreate(BaseModel):
    product_id: int
    location_id: int
    reorder_level: float
    reorder_quantity: float


class ReorderRuleResponse(BaseModel):
    id: int
    product_id: int
    location_id: int
    reorder_level: float
    reorder_quantity: float
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
