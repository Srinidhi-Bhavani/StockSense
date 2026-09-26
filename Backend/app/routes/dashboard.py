from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.product import Product
from app.models.stock import Stock
from app.models.receipt import Receipt
from app.models.delivery import Delivery
from app.models.transfer import InternalTransfer
from app.models.reorder_rule import ReorderRule
from app.models.user import User
from app.utils.auth import get_current_user


router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary")
def dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    total_products = db.query(Product).filter(
        Product.is_active == True
    ).count()

    total_stock = db.query(
        func.coalesce(func.sum(Stock.quantity), 0.0)
    ).scalar()

    out_of_stock = db.query(Stock).filter(
        Stock.quantity <= 0
    ).count()

    pending_receipts = db.query(Receipt).filter(
        Receipt.status != "Done"
    ).count()

    pending_deliveries = db.query(Delivery).filter(
        Delivery.status != "Done"
    ).count()

    pending_transfers = db.query(InternalTransfer).filter(
        InternalTransfer.status != "Done"
    ).count()

    # Reorder alerts count
    low_stock_alerts = 0
    rules = db.query(ReorderRule).all()
    for rule in rules:
        st = db.query(Stock).filter(
            Stock.product_id == rule.product_id,
            Stock.location_id == rule.location_id
        ).first()
        qty = st.quantity if st else 0.0
        if qty <= rule.reorder_level:
            low_stock_alerts += 1

    return {
        "total_products": total_products,
        "total_stock": float(total_stock),
        "out_of_stock": out_of_stock,
        "pending_receipts": pending_receipts,
        "pending_deliveries": pending_deliveries,
        "pending_transfers": pending_transfers,
        "low_stock_alerts": low_stock_alerts
    }