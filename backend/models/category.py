"""
ORM Model: ProductCategory
Table: product_categories

Groups products into logical categories (e.g., Electronics, Food, Raw Materials).
Safe-delete is enforced at the CRUD layer — a category cannot be deleted
if any active product is linked to it.
"""
from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base


class ProductCategory(Base):
    __tablename__ = "product_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    # Relationship — back-reference from Product
    products: Mapped[list["Product"]] = relationship(  # noqa: F821
        "Product", back_populates="category"
    )

    def __repr__(self) -> str:
        return f"<ProductCategory id={self.id} name={self.name!r}>"
