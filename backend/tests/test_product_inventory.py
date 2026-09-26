"""
StockSense — Comprehensive Test Suite for Product Management & Inventory Module.

Tests all 17 required scenarios:
 1. Create category
 2. Create product
 3. Add SKU
 4. Assign category
 5. Assign UOM
 6. Set initial stock
 7. Set/retrieve stock by location
 8. Update product
 9. Search by product name
10. Search by SKU
11. Filter by category
12. Filter by location
13. Detect low stock
14. Detect out of stock
15. Configure reorder level
16. Validate invalid input
17. Test duplicate SKU behavior
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app, seed_data
from database.base import Base
from database.session import get_db

from sqlalchemy.pool import StaticPool

# Use an in-memory SQLite database with StaticPool for testing
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)



def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    # Seed UOMs and default Location
    from models.uom import UnitOfMeasure
    from models.location import Location, LocationType

    with TestingSessionLocal() as db:
        uoms = [
            {"name": "Piece", "abbreviation": "pcs"},
            {"name": "Kilogram", "abbreviation": "kg"},
            {"name": "Liter", "abbreviation": "L"},
            {"name": "Box", "abbreviation": "box"},
        ]
        for u in uoms:
            if not db.query(UnitOfMeasure).filter_by(name=u["name"]).first():
                db.add(UnitOfMeasure(**u))

        locs = [
            {"name": "Main Warehouse", "code": "WH-MAIN", "location_type": LocationType.WAREHOUSE},
            {"name": "Secondary Store", "code": "STORE-02", "location_type": LocationType.STORE},
        ]
        for l in locs:
            if not db.query(Location).filter_by(code=l["code"]).first():
                db.add(Location(**l))

        db.commit()

    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


def test_1_create_category():
    response = client.post(
        "/api/v1/categories/",
        json={"name": "Electronics", "description": "Electronic gadgets and hardware"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Electronics"
    assert "id" in data


def test_2_3_4_5_create_product_with_sku_category_uom():
    # 1. Create Category
    cat_res = client.post(
        "/api/v1/categories/",
        json={"name": "Hardware"},
    )
    cat_id = cat_res.json()["id"]

    # Get a seeded UOM ID
    uom_res = client.get("/api/v1/uom/")
    uoms = uom_res.json()
    pcs_uom_id = next(u["id"] for u in uoms if u["name"] == "Piece")

    # 2. Create Product with SKU, Category, UOM
    prod_res = client.post(
        "/api/v1/products/",
        json={
            "name": "Wireless Mouse",
            "sku": "SKU-WM-100",
            "description": "Ergonomic 2.4GHz mouse",
            "category_id": cat_id,
            "uom_id": pcs_uom_id,
            "reorder_point": 10.0,
        },
    )
    assert prod_res.status_code == 201
    data = prod_res.json()
    assert data["name"] == "Wireless Mouse"
    assert data["sku"] == "SKU-WM-100"
    assert data["category_id"] == cat_id
    assert data["uom_id"] == pcs_uom_id
    assert data["reorder_point"] == 10.0


def test_6_7_initial_stock_and_stock_by_location():
    # Setup product
    uom_id = client.get("/api/v1/uom/").json()[0]["id"]
    locs = client.get("/api/v1/stock/locations").json()
    wh1_id = locs[0]["id"]
    wh2_id = locs[1]["id"]

    # Create product with initial stock in WH1
    prod_res = client.post(
        "/api/v1/products/",
        json={
            "name": "Keyboard",
            "sku": "SKU-KB-001",
            "uom_id": uom_id,
            "initial_stock": 50.0,
            "initial_location_id": wh1_id,
        },
    )
    assert prod_res.status_code == 201
    prod_id = prod_res.json()["id"]

    # Set initial stock for WH2
    stock_res = client.post(
        "/api/v1/stock/initial",
        json={
            "product_id": prod_id,
            "location_id": wh2_id,
            "quantity": 25.0,
        },
    )
    assert stock_res.status_code == 200

    # Retrieve stock breakdown for product
    levels_res = client.get(f"/api/v1/stock/product/{prod_id}")
    assert levels_res.status_code == 200
    levels = levels_res.json()
    assert len(levels) == 2

    # Check stock by location
    wh1_level = next(l for l in levels if l["location_id"] == wh1_id)
    wh2_level = next(l for l in levels if l["location_id"] == wh2_id)
    assert wh1_level["quantity"] == 50.0
    assert wh2_level["quantity"] == 25.0

    # Test GET /api/v1/stock/location/{location_id}
    loc_stock_res = client.get(f"/api/v1/stock/location/{wh1_id}")
    assert loc_stock_res.status_code == 200
    assert any(item["product_id"] == prod_id for item in loc_stock_res.json())


def test_8_update_product():
    uom_id = client.get("/api/v1/uom/").json()[0]["id"]
    prod_res = client.post(
        "/api/v1/products/",
        json={"name": "Monitor", "sku": "SKU-MON-01", "uom_id": uom_id},
    )
    prod_id = prod_res.json()["id"]

    update_res = client.put(
        f"/api/v1/products/{prod_id}",
        json={"name": "Gaming Monitor 27-inch", "reorder_point": 5.0},
    )
    assert update_res.status_code == 200
    updated_data = update_res.json()
    assert updated_data["name"] == "Gaming Monitor 27-inch"
    assert updated_data["reorder_point"] == 5.0


def test_9_10_search_by_name_and_sku():
    uom_id = client.get("/api/v1/uom/").json()[0]["id"]
    client.post(
        "/api/v1/products/",
        json={"name": "USB Cable Type-C", "sku": "SKU-CABLE-C", "uom_id": uom_id},
    )
    client.post(
        "/api/v1/products/",
        json={"name": "HDMI Cable 2m", "sku": "SKU-HDMI-02", "uom_id": uom_id},
    )

    # Search by Name
    search_name = client.get("/api/v1/products/?search=USB")
    assert search_name.status_code == 200
    items = search_name.json()["items"]
    assert len(items) == 1
    assert items[0]["name"] == "USB Cable Type-C"

    # Search by SKU
    search_sku = client.get("/api/v1/products/?search=HDMI-02")
    assert search_sku.status_code == 200
    items_sku = search_sku.json()["items"]
    assert len(items_sku) == 1
    assert items_sku[0]["sku"] == "SKU-HDMI-02"


def test_11_12_filter_by_category_and_location():
    cat1 = client.post("/api/v1/categories/", json={"name": "Cat-A"}).json()["id"]
    cat2 = client.post("/api/v1/categories/", json={"name": "Cat-B"}).json()["id"]
    uom_id = client.get("/api/v1/uom/").json()[0]["id"]
    locs = client.get("/api/v1/stock/locations").json()
    loc1_id = locs[0]["id"]

    p1 = client.post(
        "/api/v1/products/",
        json={"name": "Item A", "sku": "SKU-A", "category_id": cat1, "uom_id": uom_id, "initial_stock": 10, "initial_location_id": loc1_id},
    ).json()["id"]

    p2 = client.post(
        "/api/v1/products/",
        json={"name": "Item B", "sku": "SKU-B", "category_id": cat2, "uom_id": uom_id},
    ).json()["id"]

    # Filter by category
    res_cat1 = client.get(f"/api/v1/products/?category_id={cat1}")
    assert len(res_cat1.json()["items"]) == 1
    assert res_cat1.json()["items"][0]["id"] == p1

    # Filter by location
    res_loc = client.get(f"/api/v1/products/?location_id={loc1_id}")
    assert any(item["id"] == p1 for item in res_loc.json()["items"])


def test_13_14_detect_low_stock_and_out_of_stock():
    uom_id = client.get("/api/v1/uom/").json()[0]["id"]
    loc_id = client.get("/api/v1/stock/locations").json()[0]["id"]

    # Out of Stock product (qty = 0)
    p_out = client.post(
        "/api/v1/products/",
        json={"name": "Out of Stock Item", "sku": "SKU-OUT", "uom_id": uom_id, "reorder_point": 10.0},
    ).json()["id"]

    # Low Stock product (0 < qty <= reorder_point)
    p_low = client.post(
        "/api/v1/products/",
        json={"name": "Low Stock Item", "sku": "SKU-LOW", "uom_id": uom_id, "reorder_point": 20.0, "initial_stock": 5.0, "initial_location_id": loc_id},
    ).json()["id"]

    # Check status for Out of Stock
    res_out = client.get(f"/api/v1/products/{p_out}")
    assert res_out.json()["stock_summary"]["stock_status"] == "OUT_OF_STOCK"

    # Check status for Low Stock
    res_low = client.get(f"/api/v1/products/{p_low}")
    assert res_low.json()["stock_summary"]["stock_status"] == "LOW_STOCK"

    # Test stock status filter endpoint
    filter_low = client.get("/api/v1/products/?stock_status=LOW_STOCK")
    assert any(p["id"] == p_low for p in filter_low.json()["items"])

    filter_out = client.get("/api/v1/products/?stock_status=OUT_OF_STOCK")
    assert any(p["id"] == p_out for p in filter_out.json()["items"])


def test_15_configure_reorder_level():
    uom_id = client.get("/api/v1/uom/").json()[0]["id"]
    prod_id = client.post(
        "/api/v1/products/",
        json={"name": "Reorder Test Item", "sku": "SKU-REORDER", "uom_id": uom_id},
    ).json()["id"]

    # PATCH reorder point
    patch_res = client.patch(
        f"/api/v1/products/{prod_id}/reorder-point",
        json={"reorder_point": 15.5},
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["reorder_point"] == 15.5


def test_16_validate_invalid_input():
    uom_id = client.get("/api/v1/uom/").json()[0]["id"]

    # Empty product name
    res_empty_name = client.post(
        "/api/v1/products/",
        json={"name": "   ", "sku": "SKU-EMPTY", "uom_id": uom_id},
    )
    assert res_empty_name.status_code == 422

    # Non-existent category ID
    res_invalid_cat = client.post(
        "/api/v1/products/",
        json={"name": "Valid Name", "sku": "SKU-INV-CAT", "uom_id": uom_id, "category_id": 99999},
    )
    assert res_invalid_cat.status_code == 404

    # Non-existent UOM ID
    res_invalid_uom = client.post(
        "/api/v1/products/",
        json={"name": "Valid Name", "sku": "SKU-INV-UOM", "uom_id": 99999},
    )
    assert res_invalid_uom.status_code == 404

    # Negative initial stock
    res_neg_stock = client.post(
        "/api/v1/products/",
        json={"name": "Valid Name", "sku": "SKU-NEG", "uom_id": uom_id, "initial_stock": -50.0},
    )
    assert res_neg_stock.status_code == 422


def test_17_duplicate_sku_behavior():
    uom_id = client.get("/api/v1/uom/").json()[0]["id"]

    # First creation
    res1 = client.post(
        "/api/v1/products/",
        json={"name": "Original Product", "sku": "SKU-DUP-100", "uom_id": uom_id},
    )
    assert res1.status_code == 201

    # Duplicate creation with same SKU
    res2 = client.post(
        "/api/v1/products/",
        json={"name": "Duplicate Product", "sku": "SKU-DUP-100", "uom_id": uom_id},
    )
    assert res2.status_code == 409
    assert "already exists" in res2.json()["detail"]
