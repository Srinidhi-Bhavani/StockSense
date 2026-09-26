"""
ORM Model: StockLevel
Table: stock_levels

Tracks the available quantity of a product at a specific location.

Design notes for team members:
- One row per (product_id, location_id) pair.
- Receipts: ADD to `quantity`
- Deliveries: SUBTRACT from `quantity`
- Internal Transfers: SUBTRACT from source, ADD to destination
- Initial Stock: SET `quantity` directly (via /api/v1/stock/initial)

Never delete rows from this table — zero quantity is the correct
"out of stock" representation.
"""
from datetime import datetime

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Integer,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base


class StockLevel(Base):
    __tablename__ = "stock_levels"

    __table_args__ = (
        UniqueConstraint("product_id", "location_id", name="uq_stock_product_location"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True
    )
    location_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("locations.id", ondelete="RESTRICT"), nullable=False, index=True
    )

    quantity: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    product: Mapped["Product"] = relationship(  # noqa: F821
        "Product", back_populates="stock_levels"
    )
    location: Mapped["Location"] = relationship(  # noqa: F821
        "Location", back_populates="stock_levels"
    )

    def __repr__(self) -> str:
        return (
            f"<StockLevel product_id={self.product_id} "
            f"location_id={self.location_id} qty={self.quantity}>"
        )
