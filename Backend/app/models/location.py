from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from app.database import Base


class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    warehouse_id = Column(
        Integer,
        ForeignKey("warehouses.id"),
        nullable=False
    )
    is_active = Column(Boolean, default=True)
