"""
ORM Model: Product
Table: products

Core entity of the Product Management module.
Each product belongs to one category (optional) and one unit of measure.

Stock quantities are NOT stored on this model — they live in StockLevel
(one row per product × location pair) so stock can differ per warehouse.

Soft-delete via `is_active` flag preserves referential integrity.
"""
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base


class Product(Base):
    __tablename__ = "products"

    __table_args__ = (
        UniqueConstraint("sku", name="uq_products_sku"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    sku: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Foreign keys
    category_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("product_categories.id", ondelete="SET NULL"), nullable=True
    )
    uom_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("units_of_measure.id", ondelete="RESTRICT"), nullable=False
    )

    # Reorder / stock management
    reorder_point: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # Soft delete
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    category: Mapped["ProductCategory"] = relationship(  # noqa: F821
        "ProductCategory", back_populates="products"
    )
    uom: Mapped["UnitOfMeasure"] = relationship(  # noqa: F821
        "UnitOfMeasure", back_populates="products"
    )
    stock_levels: Mapped[list["StockLevel"]] = relationship(  # noqa: F821
        "StockLevel", back_populates="product", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Product id={self.id} sku={self.sku!r} name={self.name!r}>"
