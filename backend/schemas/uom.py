"""
Pydantic v2 schemas for UnitOfMeasure.
"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class UOMCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, examples=["Kilogram"])
    abbreviation: str = Field(..., min_length=1, max_length=20, examples=["kg"])

    @field_validator("name", "abbreviation")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        v_stripped = v.strip()
        if not v_stripped:
            raise ValueError("Field cannot be empty or whitespace only")
        return v_stripped


class UOMUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=50)
    abbreviation: str | None = Field(None, min_length=1, max_length=20)

    @field_validator("name", "abbreviation")
    @classmethod
    def validate_non_empty(cls, v: str | None) -> str | None:
        if v is not None:
            v_stripped = v.strip()
            if not v_stripped:
                raise ValueError("Field cannot be empty or whitespace only")
            return v_stripped
        return v


class UOMResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    abbreviation: str
    created_at: datetime

