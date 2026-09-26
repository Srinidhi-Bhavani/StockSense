"""
ORM Model: UnitOfMeasure
Table: units_of_measure

Stores all supported units (Piece, Kg, Liter, Box, etc.).
Seeded automatically on first startup via main.py.
"""
from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base


class UnitOfMeasure(Base):
    __tablename__ = "units_of_measure"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    abbreviation: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    # Relationship — back-reference from Product
    products: Mapped[list["Product"]] = relationship(  # noqa: F821
        "Product", back_populates="uom"
    )

    def __repr__(self) -> str:
        return f"<UnitOfMeasure id={self.id} name={self.name!r}>"
