"""
CRUD operations for Stock (StockLevel + Location).
"""
from sqlalchemy.orm import Session

from models.location import Location
from models.stock import StockLevel
from schemas.stock import InitialStockCreate, LocationCreate, StockAdjust, StockLevelResponse


# ---------------------------------------------------------------------------
# Location CRUD
# ---------------------------------------------------------------------------

def get_location(db: Session, location_id: int) -> Location | None:
    return db.query(Location).filter(Location.id == location_id).first()


def get_locations(
    db: Session, active_only: bool = True
) -> list[Location]:
    q = db.query(Location)
    if active_only:
        q = q.filter(Location.is_active.is_(True))
    return q.all()


def get_default_location(db: Session) -> Location | None:
    """Returns the first active warehouse location (used as default for initial stock)."""
    return (
        db.query(Location)
        .filter(Location.is_active.is_(True))
        .order_by(Location.id)
        .first()
    )


def create_location(db: Session, data: LocationCreate) -> Location:
    loc = Location(
        name=data.name,
        code=data.code,
        location_type=data.location_type,
    )
    db.add(loc)
    db.commit()
    db.refresh(loc)
    return loc


# ---------------------------------------------------------------------------
# StockLevel CRUD
# ---------------------------------------------------------------------------

def get_stock_for_product(db: Session, product_id: int) -> list[StockLevelResponse]:
    """Return all stock level rows for a product, enriched with location info."""
    rows = (
        db.query(StockLevel)
        .filter(StockLevel.product_id == product_id)
        .all()
    )
    result = []
    for row in rows:
        loc = get_location(db, row.location_id)
        result.append(
            StockLevelResponse(
                id=row.id,
                product_id=row.product_id,
                location_id=row.location_id,
                quantity=row.quantity,
                updated_at=row.updated_at,
                location_name=loc.name if loc else None,
                location_code=loc.code if loc else None,
            )
        )
    return result


def get_total_stock_for_product(db: Session, product_id: int) -> float:
    """Sum of quantity across all locations for a product."""
    rows = db.query(StockLevel).filter(StockLevel.product_id == product_id).all()
    return sum(r.quantity for r in rows)


def get_stock_quantity_at_location(db: Session, product_id: int, location_id: int) -> float:
    """Quantity of a specific product at a specific location."""
    sl = (
        db.query(StockLevel)
        .filter(StockLevel.product_id == product_id, StockLevel.location_id == location_id)
        .first()
    )
    return sl.quantity if sl else 0.0


def get_stock_for_location(db: Session, location_id: int) -> list[StockLevelResponse]:
    """Return all stock level rows for a specific location across all products."""
    loc = get_location(db, location_id)
    rows = db.query(StockLevel).filter(StockLevel.location_id == location_id).all()
    result = []
    for row in rows:
        result.append(
            StockLevelResponse(
                id=row.id,
                product_id=row.product_id,
                location_id=row.location_id,
                quantity=row.quantity,
                updated_at=row.updated_at,
                location_name=loc.name if loc else None,
                location_code=loc.code if loc else None,
            )
        )
    return result



def get_or_create_stock_level(
    db: Session, product_id: int, location_id: int
) -> StockLevel:
    """Get existing StockLevel row or create one with qty=0."""
    sl = (
        db.query(StockLevel)
        .filter(
            StockLevel.product_id == product_id,
            StockLevel.location_id == location_id,
        )
        .first()
    )
    if not sl:
        sl = StockLevel(product_id=product_id, location_id=location_id, quantity=0.0)
        db.add(sl)
        db.commit()
        db.refresh(sl)
    return sl


def set_initial_stock(db: Session, data: InitialStockCreate) -> StockLevel:
    """
    Set (overwrite) the quantity for a product at a location.
    Intended for initial stock entry only — use adjust_stock for movements.
    """
    sl = get_or_create_stock_level(db, data.product_id, data.location_id)
    sl.quantity = data.quantity
    db.commit()
    db.refresh(sl)
    return sl


def adjust_stock(db: Session, data: StockAdjust) -> StockLevel:
    """
    Delta-based adjustment. Called by:
      - Receipts: positive delta
      - Deliveries: negative delta
      - Internal Transfers: subtract from source, add to destination
    Returns updated StockLevel row.
    """
    sl = get_or_create_stock_level(db, data.product_id, data.location_id)
    new_qty = sl.quantity + data.delta
    if new_qty < 0:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"Insufficient stock at location {data.location_id}. "
                f"Available: {sl.quantity}, Requested: {abs(data.delta)}"
            ),
        )
    sl.quantity = new_qty
    db.commit()
    db.refresh(sl)
    return sl
