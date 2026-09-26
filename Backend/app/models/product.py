from sqlalchemy import Column, Integer, String, Float, Boolean
from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    sku = Column(String, unique=True, index=True, nullable=False)
    category = Column(String, nullable=False)
    uom = Column(String, nullable=False)
    initial_stock = Column(Float, default=0)
    is_active = Column(Boolean, default=True)