from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database import Base


class InternalTransfer(Base):
    __tablename__ = "transfers"

    id = Column(Integer, primary_key=True, index=True)
    source_warehouse_id = Column(
        Integer,
        ForeignKey("warehouses.id"),
        nullable=False
    )
    destination_warehouse_id = Column(
        Integer,
        ForeignKey("warehouses.id"),
        nullable=False
    )
    source_location_id = Column(
        Integer,
        ForeignKey("locations.id"),
        nullable=False
    )
    destination_location_id = Column(
        Integer,
        ForeignKey("locations.id"),
        nullable=False
    )
    status = Column(String, default="Draft")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    items = relationship("TransferItem", backref="transfer", cascade="all, delete-orphan")


Transfer = InternalTransfer


class TransferItem(Base):
    __tablename__ = "transfer_items"

    id = Column(Integer, primary_key=True, index=True)
    transfer_id = Column(
        Integer,
        ForeignKey("transfers.id"),
        nullable=False
    )
    product_id = Column(
        Integer,
        ForeignKey("products.id"),
        nullable=False
    )
    quantity = Column(Float, nullable=False)