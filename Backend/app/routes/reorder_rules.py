from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.reorder_rule import ReorderRule
from app.models.product import Product
from app.models.location import Location
from app.models.user import User
from app.schemas.reorder_rule import ReorderRuleCreate, ReorderRuleResponse
from app.utils.auth import get_current_user


router = APIRouter(prefix="/reorder-rules", tags=["Reorder Rules"])


@router.post("/", response_model=ReorderRuleResponse)
def set_reorder_rule(
    data: ReorderRuleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verify product and location exist
    prod = db.query(Product).filter(Product.id == data.product_id).first()
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")

    loc = db.query(Location).filter(Location.id == data.location_id).first()
    if not loc:
        raise HTTPException(status_code=404, detail="Location not found")

    if data.reorder_level < 0 or data.reorder_quantity <= 0:
        raise HTTPException(status_code=400, detail="Invalid reorder level or quantity")

    rule = db.query(ReorderRule).filter(
        ReorderRule.product_id == data.product_id,
        ReorderRule.location_id == data.location_id
    ).first()

    if rule:
        rule.reorder_level = data.reorder_level
        rule.reorder_quantity = data.reorder_quantity
    else:
        rule = ReorderRule(
            product_id=data.product_id,
            location_id=data.location_id,
            reorder_level=data.reorder_level,
            reorder_quantity=data.reorder_quantity
        )
        db.add(rule)

    db.commit()
    db.refresh(rule)
    return rule


@router.get("/", response_model=List[ReorderRuleResponse])
def get_reorder_rules(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(ReorderRule).all()


@router.delete("/{rule_id}")
def delete_reorder_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    rule = db.query(ReorderRule).filter(ReorderRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Reorder rule not found")

    db.delete(rule)
    db.commit()
    return {"message": "Reorder rule deleted successfully", "rule_id": rule_id}
