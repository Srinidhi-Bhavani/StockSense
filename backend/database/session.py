"""
SQLAlchemy engine + session factory.
Import `get_db` as a FastAPI dependency in route functions.
"""
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

import config

# ---------------------------------------------------------------------------
# Engine
# SQLite-specific: check_same_thread=False allows usage across multiple
# threads (required by FastAPI's synchronous thread pool).
# ---------------------------------------------------------------------------
connect_args: dict = {}
if config.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    config.DATABASE_URL,
    connect_args=connect_args,
    echo=False,  # Set True to log SQL statements during debugging
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ---------------------------------------------------------------------------
# FastAPI dependency — yields a DB session per request
# ---------------------------------------------------------------------------
def get_db() -> Generator[Session, None, None]:
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
