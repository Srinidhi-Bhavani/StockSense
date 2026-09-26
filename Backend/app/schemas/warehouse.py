from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class WarehouseCreate(BaseModel):
    name: str
    location: str


class LocationCreate(BaseModel):
    name: str
    warehouse_id: int


class LocationResponse(BaseModel):
    id: int
    name: str
    warehouse_id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class WarehouseResponse(BaseModel):
    id: int
    name: str
    location: str
    is_active: bool
    created_at: Optional[datetime] = None
    locations: Optional[List[LocationResponse]] = []

    class Config:
        from_attributes = True