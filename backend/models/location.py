"""
ORM Model: Location
Table: locations

Represents warehouses, stores, or virtual locations.
This table is the shared foundation for stock-by-location.

Other team members (Receipts, Deliveries, Internal Transfers) reference
this table via FK in their own transaction models — they do NOT need to
create their own location table.

Seeded with a default 'Main Warehouse' on first startup.
"""
import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base


class LocationType(str, enum.Enum):
    WAREHOUSE = "WAREHOUSE"
    STORE = "STORE"
    VIRTUAL = "VIRTUAL"


class Location(Base):
    __tablename__ = "locations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    location_type: Mapped[LocationType] = mapped_column(
        Enum(LocationType), default=LocationType.WAREHOUSE, nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    # Relationship
    stock_levels: Mapped[list["StockLevel"]] = relationship(  # noqa: F821
        "StockLevel", back_populates="location"
    )

    def __repr__(self) -> str:
        return f"<Location id={self.id} code={self.code!r}>"
