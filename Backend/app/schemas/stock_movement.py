from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class StockMovementResponse(BaseModel):
    id: int
    product_id: int
    warehouse_id: int
    source_location_id: Optional[int] = None
    destination_location_id: Optional[int] = None
    movement_type: str
    operation_type: Optional[str] = None
    quantity: float
    reference_id: Optional[int] = None
    timestamp: datetime

    class Config:
        from_attributes = True
