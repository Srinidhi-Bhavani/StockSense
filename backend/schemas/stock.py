"""
Pydantic v2 schemas for Stock (StockLevel + Location).
"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from models.location import LocationType


# ---------------------------------------------------------------------------
# Location schemas
# ---------------------------------------------------------------------------

class LocationCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, examples=["Main Warehouse"])
    code: str = Field(..., min_length=1, max_length=20, examples=["WH-MAIN"])
    location_type: LocationType = LocationType.WAREHOUSE


class LocationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    code: str
    location_type: LocationType
    is_active: bool
    created_at: datetime


# ---------------------------------------------------------------------------
# StockLevel schemas
# ---------------------------------------------------------------------------

class InitialStockCreate(BaseModel):
    """Set the opening / initial stock quantity for a product at a location."""
    product_id: int = Field(..., gt=0)
    location_id: int = Field(..., gt=0)
    quantity: float = Field(..., ge=0.0, examples=[100.0])


class StockAdjust(BaseModel):
    """
    Delta-based stock adjustment.
    Used by Receipts (positive delta) and Deliveries (negative delta).
    Internal Transfers will call this twice — subtract from source, add to dest.
    """
    product_id: int = Field(..., gt=0)
    location_id: int = Field(..., gt=0)
    delta: float = Field(..., examples=[50.0, -25.0])
    reason: str | None = Field(None, examples=["Receipt #001"])


class StockLevelResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    location_id: int
    quantity: float
    updated_at: datetime

    # Enriched from joined data
    location_name: str | None = None
    location_code: str | None = None
