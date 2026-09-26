"""
CRUD operations for UnitOfMeasure.
"""
from sqlalchemy.orm import Session

from models.uom import UnitOfMeasure
from schemas.uom import UOMCreate, UOMUpdate


def get_uom(db: Session, uom_id: int) -> UnitOfMeasure | None:
    return db.query(UnitOfMeasure).filter(UnitOfMeasure.id == uom_id).first()


def get_uom_by_name(db: Session, name: str) -> UnitOfMeasure | None:
    return db.query(UnitOfMeasure).filter(UnitOfMeasure.name == name).first()


def get_uoms(db: Session, skip: int = 0, limit: int = 100) -> list[UnitOfMeasure]:
    return db.query(UnitOfMeasure).offset(skip).limit(limit).all()


def create_uom(db: Session, data: UOMCreate) -> UnitOfMeasure:
    uom = UnitOfMeasure(name=data.name, abbreviation=data.abbreviation)
    db.add(uom)
    db.commit()
    db.refresh(uom)
    return uom


def update_uom(db: Session, uom_id: int, data: UOMUpdate) -> UnitOfMeasure | None:
    uom = get_uom(db, uom_id)
    if not uom:
        return None
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(uom, field, value)
    db.commit()
    db.refresh(uom)
    return uom


def delete_uom(db: Session, uom_id: int) -> tuple[bool, str]:
    """
    Safe-delete: refuses if any active product is using this UOM.
    Returns (success, message).
    """
    uom = get_uom(db, uom_id)
    if not uom:
        return False, "UOM not found"
    active_products = [p for p in uom.products if p.is_active]
    if active_products:
        return False, (
            f"Cannot delete '{uom.name}' — "
            f"{len(active_products)} active product(s) are using this unit of measure."
        )
    db.delete(uom)
    db.commit()
    return True, "Deleted successfully"
