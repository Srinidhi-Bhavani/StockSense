from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database import Base


class Delivery(Base):
    __tablename__ = "deliveries"

    id = Column(Integer, primary_key=True, index=True)
    customer_reference = Column(String, nullable=False)
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

    items = relationship("DeliveryItem", backref="delivery", cascade="all, delete-orphan")


class DeliveryItem(Base):
    __tablename__ = "delivery_items"

    id = Column(Integer, primary_key=True, index=True)
    delivery_id = Column(
        Integer,
        ForeignKey("deliveries.id"),
        nullable=False
    )
    product_id = Column(
        Integer,
        ForeignKey("products.id"),
        nullable=False
    )
    quantity = Column(Float, nullable=False)