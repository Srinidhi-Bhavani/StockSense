"""
Pydantic v2 schemas for ProductCategory.
"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, examples=["Electronics"])
    description: str | None = Field(None, examples=["Electronic components and devices"])

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v_stripped = v.strip()
        if not v_stripped:
            raise ValueError("Category name cannot be empty or whitespace only")
        return v_stripped


class CategoryUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str | None) -> str | None:
        if v is not None:
            v_stripped = v.strip()
            if not v_stripped:
                raise ValueError("Category name cannot be empty or whitespace only")
            return v_stripped
        return v


class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    created_at: datetime


class CategoryWithProductCount(CategoryResponse):
    """Extended response that includes how many products belong to this category."""
    product_count: int = 0

