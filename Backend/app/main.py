from fastapi import FastAPI
from app.database import Base, engine
from app import models

from app.routes.receipts import router as receipt_router
from app.routes.deliveries import router as delivery_router
from app.routes.transfers import router as transfer_router
from app.routes.stock_movements import router as stock_movement_router

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="StockSense API",
    description="Inventory Management System - Person 3 Workflows (Receipts, Deliveries, Transfers, Movement History)",
    version="1.0.0"
)

# Register API routes
app.include_router(receipt_router)
app.include_router(delivery_router)
app.include_router(transfer_router)
app.include_router(stock_movement_router)


@app.get("/")
def root():
    return {
        "message": "StockSense API is running!"
    }