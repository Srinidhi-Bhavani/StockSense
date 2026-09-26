from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime
from sqlalchemy.orm import synonym
from app.database import Base


class StockMovement(Base):
    __tablename__ = "stock_movements"

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
    source_location_id = Column(
        Integer,
        ForeignKey("locations.id"),
        nullable=True
    )
    destination_location_id = Column(
        Integer,
        ForeignKey("locations.id"),
        nullable=True
    )
    movement_type = Column(String, nullable=False)
    quantity = Column(Float, nullable=False)
    reference_id = Column(Integer, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    operation_type = synonym("movement_type")