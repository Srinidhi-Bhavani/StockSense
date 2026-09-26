from sqlalchemy import Column, Integer, Float, ForeignKey
from app.database import Base


class ReorderRule(Base):
    __tablename__ = "reorder_rules"

    id = Column(Integer, primary_key=True, index=True)

    product_id = Column(
        Integer,
        ForeignKey("products.id"),
        nullable=False
    )

    warehouse_id = Column(
        Integer,
        ForeignKey("warehouses.id"),
        nullable=False
    )

    minimum_quantity = Column(Float, nullable=False)
    reorder_quantity = Column(Float, nullable=False)