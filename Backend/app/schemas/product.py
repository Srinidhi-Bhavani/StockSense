from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ProductCreate(BaseModel):
    name: str
    sku: str
    category: Optional[str] = None
    category_id: Optional[int] = None
    uom: str
    initial_stock: float = 0.0


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    sku: Optional[str] = None
    category: Optional[str] = None
    category_id: Optional[int] = None
    uom: Optional[str] = None
    initial_stock: Optional[float] = None
    is_active: Optional[bool] = None


class ProductResponse(BaseModel):
    id: int
    name: str
    sku: str
    category: Optional[str] = None
    category_id: Optional[int] = None
    uom: str
    initial_stock: float
    is_active: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True