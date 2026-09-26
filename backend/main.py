"""
StockSense — FastAPI Application Entry Point
============================================
Run with:
    cd backend
    uvicorn main:app --reload

Swagger UI:  http://127.0.0.1:8000/docs
ReDoc:       http://127.0.0.1:8000/redoc
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import config

# ---------------------------------------------------------------------------
# Import all models before create_all so metadata is populated
# ---------------------------------------------------------------------------
import models  # noqa: F401 — side-effect import registers all ORM models
from database.base import Base
from database.session import engine

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
from routers.uom import router as uom_router
from routers.categories import router as categories_router
from routers.products import router as products_router
from routers.stock import router as stock_router


# ---------------------------------------------------------------------------
# Seed Data
# ---------------------------------------------------------------------------

DEFAULT_UOMS = [
    {"name": "Piece",  "abbreviation": "pcs"},
    {"name": "Unit",   "abbreviation": "unit"},
    {"name": "Kilogram", "abbreviation": "kg"},
    {"name": "Gram",   "abbreviation": "g"},
    {"name": "Liter",  "abbreviation": "L"},
    {"name": "Milliliter", "abbreviation": "mL"},
    {"name": "Box",    "abbreviation": "box"},
    {"name": "Dozen",  "abbreviation": "doz"},
    {"name": "Meter",  "abbreviation": "m"},
    {"name": "Pair",   "abbreviation": "pair"},
]

DEFAULT_LOCATION = {
    "name": "Main Warehouse",
    "code": "WH-MAIN",
    "location_type": "WAREHOUSE",
}


def seed_data() -> None:
    """
    Seed the database with default UOMs and the Main Warehouse location
    if they don't already exist. Safe to call on every startup.
    """
    from sqlalchemy.orm import Session
    from models.uom import UnitOfMeasure
    from models.location import Location, LocationType

    with Session(engine) as db:
        # Seed UOMs
        for uom_data in DEFAULT_UOMS:
            exists = db.query(UnitOfMeasure).filter_by(name=uom_data["name"]).first()
            if not exists:
                db.add(UnitOfMeasure(**uom_data))

        # Seed default location
        loc_exists = db.query(Location).filter_by(code=DEFAULT_LOCATION["code"]).first()
        if not loc_exists:
            db.add(
                Location(
                    name=DEFAULT_LOCATION["name"],
                    code=DEFAULT_LOCATION["code"],
                    location_type=LocationType.WAREHOUSE,
                )
            )

        db.commit()
    print("[OK] Seed data applied (UOMs + default location)")


# ---------------------------------------------------------------------------
# Lifespan — runs on startup / shutdown
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)
    print("[OK] Database tables created / verified")
    seed_data()
    yield
    # Shutdown (nothing needed for SQLite)


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(
    title=config.PROJECT_NAME,
    version=config.VERSION,
    description=config.DESCRIPTION,
    lifespan=lifespan,
)

# CORS — allow all origins during hackathon development
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Mount Routers
# ---------------------------------------------------------------------------

app.include_router(uom_router, prefix=config.API_PREFIX)
app.include_router(categories_router, prefix=config.API_PREFIX)
app.include_router(products_router, prefix=config.API_PREFIX)
app.include_router(stock_router, prefix=config.API_PREFIX)


# ---------------------------------------------------------------------------
# Root & Health endpoints
# ---------------------------------------------------------------------------

@app.get("/", tags=["Root"])
def root() -> dict:
    return {
        "project": config.PROJECT_NAME,
        "version": config.VERSION,
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", tags=["Root"])
def health() -> dict:
    return {"status": "ok", "service": config.PROJECT_NAME}
