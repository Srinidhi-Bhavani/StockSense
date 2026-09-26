from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app import models

# Import routers
from app.routes.auth import router as auth_router
from app.routes.categories import router as categories_router
from app.routes.products import router as products_router
from app.routes.warehouse import router as warehouse_router
from app.routes.stock import router as stock_router
from app.routes.receipts import router as receipts_router
from app.routes.deliveries import router as deliveries_router
from app.routes.transfers import router as transfers_router
from app.routes.reorder_rules import router as reorder_rules_router
from app.routes.dashboard import router as dashboard_router

# Initialize database tables and schema migrations
init_db()

app = FastAPI(
    title="StockSense API",
    description="StockSense Inventory Management System - REST Backend",
    version="1.0.0"
)

# Enable CORS for React frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for local hackathon development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount all routers
app.include_router(auth_router)
app.include_router(categories_router)
app.include_router(products_router)
app.include_router(warehouse_router)
app.include_router(stock_router)
app.include_router(receipts_router)
app.include_router(deliveries_router)
app.include_router(transfers_router)
app.include_router(reorder_rules_router)
app.include_router(dashboard_router)


@app.get("/")
def root():
    return {
        "message": "StockSense Backend is running!",
        "version": "1.0.0",
        "docs_url": "/docs"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}