from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class StockResponse(BaseModel):
    id: int
    product_id: int
    location_id: int
    quantity: float
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class StockAdjustmentRequest(BaseModel):
    product_id: int
    location_id: int
    actual_quantity: float
    reason: str


class StockAdjustmentResponse(BaseModel):
    id: int
    product_id: int
    location_id: int
    quantity: float
    actual_quantity: Optional[float] = None
    old_quantity: Optional[float] = 0.0
    difference: Optional[float] = 0.0
    reason: str
    adjusted_by: Optional[int] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class StockMovementResponse(BaseModel):
    id: int
    product_id: int
    quantity: float
    source_location_id: Optional[int] = None
    destination_location_id: Optional[int] = None
    operation_type: str
    reference_id: Optional[int] = None
    user_id: Optional[int] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ReorderAlertResponse(BaseModel):
    product_id: int
    product_name: str
    sku: str
    location_id: int
    location_name: str
    current_stock: float
    reorder_level: float
    reorder_quantity: float