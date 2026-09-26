"""
CRUD operations for ProductCategory.
"""
from sqlalchemy.orm import Session

from models.category import ProductCategory
from schemas.category import CategoryCreate, CategoryUpdate


def get_category(db: Session, category_id: int) -> ProductCategory | None:
    return db.query(ProductCategory).filter(ProductCategory.id == category_id).first()


def get_category_by_name(db: Session, name: str) -> ProductCategory | None:
    return db.query(ProductCategory).filter(ProductCategory.name == name).first()


def get_categories(
    db: Session, skip: int = 0, limit: int = 100
) -> list[ProductCategory]:
    return db.query(ProductCategory).offset(skip).limit(limit).all()


def count_products_in_category(db: Session, category_id: int) -> int:
    cat = get_category(db, category_id)
    if not cat:
        return 0
    return len([p for p in cat.products if p.is_active])


def create_category(db: Session, data: CategoryCreate) -> ProductCategory:
    cat = ProductCategory(name=data.name, description=data.description)
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


def update_category(
    db: Session, category_id: int, data: CategoryUpdate
) -> ProductCategory | None:
    cat = get_category(db, category_id)
    if not cat:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(cat, field, value)
    db.commit()
    db.refresh(cat)
    return cat


def delete_category(db: Session, category_id: int) -> tuple[bool, str]:
    """
    Safe-delete: refuses if active products are linked to this category.
    Returns (success, message).
    """
    cat = get_category(db, category_id)
    if not cat:
        return False, "Category not found"
    active_products = [p for p in cat.products if p.is_active]
    if active_products:
        return False, (
            f"Cannot delete '{cat.name}' — "
            f"{len(active_products)} active product(s) are linked to this category. "
            "Reassign or deactivate them first."
        )
    db.delete(cat)
    db.commit()
    return True, "Deleted successfully"
