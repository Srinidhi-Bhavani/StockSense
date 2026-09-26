from fastapi import FastAPI
from app.database import Base, engine
from app import models

from app.routes.receipts import router as receipt_router

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="StockSense",
    version="1.0.0"
)

# Register API routes
app.include_router(receipt_router)


@app.get("/")
def root():
    return {
        "message": "StockSense Backend is running!"
    }