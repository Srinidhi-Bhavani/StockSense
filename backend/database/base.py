"""
SQLAlchemy Declarative Base.
All ORM models import this Base so that a single
Base.metadata.create_all(engine) call creates every table.
"""
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
