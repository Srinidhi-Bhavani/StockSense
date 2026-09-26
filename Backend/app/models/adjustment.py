from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class StockAdjustment(Base):
    __tablename__ = "stock_adjustments"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    quantity = Column(Float, nullable=False)  # Actual counted quantity
    old_quantity = Column(Float, nullable=True, default=0.0)
    difference = Column(Float, nullable=True, default=0.0)
    reason = Column(String, nullable=False)
    adjusted_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    @property
    def actual_quantity(self) -> float:
        return self.quantity

    product = relationship("Product")
    location = relationship("Location")
    user = relationship("User")