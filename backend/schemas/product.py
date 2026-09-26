"""
Pydantic v2 schemas for Product.
Includes the computed stock_status field derived from
total quantity vs reorder_point.
"""
import enum
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from schemas.uom import UOMResponse
from schemas.category import CategoryResponse


# ---------------------------------------------------------------------------
# Stock Status Enum
# ---------------------------------------------------------------------------

class StockStatus(str, enum.Enum):
    IN_STOCK = "IN_STOCK"
    LOW_STOCK = "LOW_STOCK"
    OUT_OF_STOCK = "OUT_OF_STOCK"


# ---------------------------------------------------------------------------
# Request Schemas
# ---------------------------------------------------------------------------

class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, examples=["Wireless Mouse"])
    sku: str = Field(..., min_length=1, max_length=100, examples=["SKU-WM-001"])
    description: str | None = Field(None, examples=["Ergonomic wireless mouse, 2.4GHz"])
    category_id: int | None = Field(None, gt=0)
    uom_id: int = Field(..., gt=0)
    reorder_point: float = Field(default=0.0, ge=0.0, examples=[10.0])
    # Initial stock — recorded at the default warehouse on product creation
    initial_stock: float = Field(default=0.0, ge=0.0, examples=[50.0])
    initial_location_id: int | None = Field(
        None,
        gt=0,
        description="Location for initial stock. Defaults to the Main Warehouse.",
    )

    @field_validator("name", "sku")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        v_stripped = v.strip()
        if not v_stripped:
            raise ValueError("Field cannot be empty or whitespace only")
        return v_stripped


class ProductUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=200)
    sku: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = None
    category_id: int | None = Field(None, gt=0)
    uom_id: int | None = Field(None, gt=0)
    reorder_point: float | None = Field(None, ge=0.0)
    is_active: bool | None = None

    @field_validator("name", "sku")
    @classmethod
    def validate_non_empty(cls, v: str | None) -> str | None:
        if v is not None:
            v_stripped = v.strip()
            if not v_stripped:
                raise ValueError("Field cannot be empty or whitespace only")
            return v_stripped
        return v


class ReorderPointUpdate(BaseModel):
    reorder_point: float = Field(..., ge=0.0, description="Minimum stock reorder point threshold")



# ---------------------------------------------------------------------------
# Response Schemas
# ---------------------------------------------------------------------------

class StockSummary(BaseModel):
    """Aggregated stock info across all locations."""
    total_quantity: float
    stock_status: StockStatus
    reorder_point: float


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    sku: str
    description: str | None
    category_id: int | None
    uom_id: int
    reorder_point: float
    is_active: bool
    created_at: datetime
    updated_at: datetime

    # Nested objects
    category: CategoryResponse | None = None
    uom: UOMResponse | None = None


class ProductDetailResponse(ProductResponse):
    """Full product detail including stock summary and per-location breakdown."""
    stock_summary: StockSummary | None = None


class ProductListResponse(BaseModel):
    """Paginated list wrapper."""
    total: int
    skip: int
    limit: int
    items: list[ProductResponse]
