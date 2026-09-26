"""
CRUD operations for Product.
Handles full lifecycle: create, read, update, soft-delete, search, filter.
Stock status is computed from StockLevel aggregate + reorder_point.
"""
from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from models.product import Product
from models.stock import StockLevel
from schemas.product import ProductCreate, ProductUpdate, StockStatus
from schemas.product import StockSummary
import crud.stock as stock_crud


# ---------------------------------------------------------------------------
# Stock Status Helper
# ---------------------------------------------------------------------------

def compute_stock_status(total_qty: float, reorder_point: float) -> StockStatus:
    """
    IN_STOCK   : qty > reorder_point
    LOW_STOCK  : 0 < qty <= reorder_point
    OUT_OF_STOCK: qty == 0
    """
    if total_qty <= 0:
        return StockStatus.OUT_OF_STOCK
    if total_qty <= reorder_point:
        return StockStatus.LOW_STOCK
    return StockStatus.IN_STOCK


def build_stock_summary(
    db: Session, product: Product, location_id: int | None = None
) -> StockSummary:
    if location_id is not None:
        qty = stock_crud.get_stock_quantity_at_location(db, product.id, location_id)
    else:
        qty = stock_crud.get_total_stock_for_product(db, product.id)

    return StockSummary(
        total_quantity=qty,
        stock_status=compute_stock_status(qty, product.reorder_point),
        reorder_point=product.reorder_point,
    )


# ---------------------------------------------------------------------------
# Read
# ---------------------------------------------------------------------------

def get_product(db: Session, product_id: int) -> Product | None:
    return (
        db.query(Product)
        .options(joinedload(Product.category), joinedload(Product.uom))
        .filter(Product.id == product_id, Product.is_active.is_(True))
        .first()
    )


def get_products(
    db: Session,
    *,
    search: str | None = None,
    category_id: int | None = None,
    uom_id: int | None = None,
    location_id: int | None = None,
    stock_status: StockStatus | None = None,
    active_only: bool = True,
    skip: int = 0,
    limit: int = 50,
) -> tuple[list[Product], int]:
    """
    Returns (items, total_count) for pagination.
    Supports search by name / SKU and filters by category, UOM, location, stock_status.
    """
    q = (
        db.query(Product)
        .options(joinedload(Product.category), joinedload(Product.uom))
    )

    if active_only:
        q = q.filter(Product.is_active.is_(True))

    if search:
        pattern = f"%{search.strip()}%"
        q = q.filter(
            or_(
                Product.name.ilike(pattern),
                Product.sku.ilike(pattern),
            )
        )

    if category_id is not None:
        q = q.filter(Product.category_id == category_id)

    if uom_id is not None:
        q = q.filter(Product.uom_id == uom_id)

    if location_id is not None:
        q = q.join(StockLevel, Product.id == StockLevel.product_id).filter(
            StockLevel.location_id == location_id
        )

    total = q.count()
    products = q.offset(skip).limit(limit).all()

    # Filter by stock_status post-query (requires evaluating stock)
    if stock_status is not None:
        filtered = []
        for p in products:
            if location_id is not None:
                qty = stock_crud.get_stock_quantity_at_location(db, p.id, location_id)
            else:
                qty = stock_crud.get_total_stock_for_product(db, p.id)

            status = compute_stock_status(qty, p.reorder_point)
            if status == stock_status:
                filtered.append(p)
        return filtered, len(filtered)

    return products, total


# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------

def create_product(db: Session, data: ProductCreate) -> Product:
    product = Product(
        name=data.name,
        sku=data.sku,
        description=data.description,
        category_id=data.category_id,
        uom_id=data.uom_id,
        reorder_point=data.reorder_point,
    )
    db.add(product)
    db.commit()
    db.refresh(product)

    # Record initial stock
    if data.initial_stock > 0 or data.initial_location_id:
        location_id = data.initial_location_id
        if not location_id:
            default_loc = stock_crud.get_default_location(db)
            location_id = default_loc.id if default_loc else None

        if location_id:
            from schemas.stock import InitialStockCreate
            stock_crud.set_initial_stock(
                db,
                InitialStockCreate(
                    product_id=product.id,
                    location_id=location_id,
                    quantity=data.initial_stock,
                ),
            )

    # Reload with relationships
    db.refresh(product)
    return product


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------

def update_product(
    db: Session, product_id: int, data: ProductUpdate
) -> Product | None:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    return product


# ---------------------------------------------------------------------------
# Delete (soft)
# ---------------------------------------------------------------------------

def delete_product(db: Session, product_id: int) -> tuple[bool, str]:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return False, "Product not found"
    if not product.is_active:
        return False, "Product is already deactivated"
    product.is_active = False
    db.commit()
    return True, f"Product '{product.name}' has been deactivated"


# ---------------------------------------------------------------------------
# Reorder check
# ---------------------------------------------------------------------------

def get_products_needing_reorder(db: Session) -> list[dict]:
    """
    Returns products where total stock <= reorder_point.
    Used by the dashboard / alerts to flag items needing reorder.
    """
    products = (
        db.query(Product)
        .options(joinedload(Product.category), joinedload(Product.uom))
        .filter(Product.is_active.is_(True), Product.reorder_point > 0)
        .all()
    )
    results = []
    for p in products:
        total_qty = stock_crud.get_total_stock_for_product(db, p.id)
        status = compute_stock_status(total_qty, p.reorder_point)
        if status in (StockStatus.LOW_STOCK, StockStatus.OUT_OF_STOCK):
            results.append(
                {
                    "product_id": p.id,
                    "name": p.name,
                    "sku": p.sku,
                    "total_quantity": total_qty,
                    "reorder_point": p.reorder_point,
                    "stock_status": status,
                }
            )
    return results
