from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///./stocksense.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)

    # Safe schema evolution for SQLite (adds missing columns if upgrading existing db)
    migrations = [
        ("users", "role", "VARCHAR DEFAULT 'staff'"),
        ("users", "created_at", "DATETIME"),
        ("products", "category_id", "INTEGER"),
        ("products", "created_at", "DATETIME"),
        ("warehouses", "created_at", "DATETIME"),
        ("locations", "created_at", "DATETIME"),
        ("stock", "updated_at", "DATETIME"),
        ("receipts", "reference_no", "VARCHAR"),
        ("receipts", "created_at", "DATETIME"),
        ("deliveries", "reference_no", "VARCHAR"),
        ("deliveries", "created_at", "DATETIME"),
        ("transfers", "reference_no", "VARCHAR"),
        ("transfers", "created_at", "DATETIME"),
        ("stock_adjustments", "old_quantity", "FLOAT DEFAULT 0.0"),
        ("stock_adjustments", "difference", "FLOAT DEFAULT 0.0"),
        ("stock_adjustments", "adjusted_by", "INTEGER"),
        ("stock_adjustments", "created_at", "DATETIME"),
        ("stock_movements", "user_id", "INTEGER"),
        ("stock_movements", "created_at", "DATETIME"),
        ("reorder_rules", "created_at", "DATETIME"),
    ]
    with engine.connect() as conn:
        for table, col, col_type in migrations:
            try:
                cols = [row[1] for row in conn.exec_driver_sql(f"PRAGMA table_info({table});").fetchall()]
                if cols and col not in cols:
                    conn.exec_driver_sql(f"ALTER TABLE {table} ADD COLUMN {col} {col_type};")
            except Exception:
                pass
        conn.commit()