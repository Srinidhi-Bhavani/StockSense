from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database import Base


class Receipt(Base):
    __tablename__ = "receipts"

    id = Column(Integer, primary_key=True, index=True)
    supplier = Column(String, nullable=False)
    warehouse_id = Column(
        Integer,
        ForeignKey("warehouses.id"),
        nullable=False
    )
    location_id = Column(
        Integer,
        ForeignKey("locations.id"),
        nullable=False
    )
    status = Column(String, default="Draft")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    items = relationship("ReceiptItem", backref="receipt", cascade="all, delete-orphan")


class ReceiptItem(Base):
    __tablename__ = "receipt_items"

    id = Column(Integer, primary_key=True, index=True)
    receipt_id = Column(
        Integer,
        ForeignKey("receipts.id"),
        nullable=False
    )
    product_id = Column(
        Integer,
        ForeignKey("products.id"),
        nullable=False
    )
    quantity = Column(Float, nullable=False)