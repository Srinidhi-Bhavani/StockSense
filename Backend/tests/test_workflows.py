import os
import sys
import unittest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add Backend to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import Base, get_db
from app.main import app
from app.models.warehouse import Warehouse
from app.models.location import Location
from app.models.product import Product
from app.models.stock import Stock
from app.models.stock_movement import StockMovement

from sqlalchemy.pool import StaticPool

# Test SQLite in-memory database with StaticPool
TEST_DB_URL = "sqlite://"
test_engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


class TestStockSenseWorkflows(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=test_engine)
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        Base.metadata.drop_all(bind=test_engine)

    def setUp(self):
        # Clear data before each test
        db = TestingSessionLocal()
        for table in reversed(Base.metadata.sorted_tables):
            db.execute(table.delete())
        db.commit()

        # Seed initial master data: Warehouses, Locations, Products
        self.wh_a = Warehouse(name="Warehouse A", location="Building 1", is_active=True)
        self.wh_b = Warehouse(name="Warehouse B", location="Building 2", is_active=True)
        db.add_all([self.wh_a, self.wh_b])
        db.flush()

        self.loc_a1 = Location(name="Rack A1", warehouse_id=self.wh_a.id)
        self.loc_a2 = Location(name="Rack A2", warehouse_id=self.wh_a.id)
        self.loc_b1 = Location(name="Rack B1", warehouse_id=self.wh_b.id)
        db.add_all([self.loc_a1, self.loc_a2, self.loc_b1])
        db.flush()

        self.prod_rod = Product(name="Steel Rod", sku="STEEL-001", category="Raw Material", uom="Units", initial_stock=0)
        self.prod_chair = Product(name="Office Chair", sku="CHAIR-001", category="Finished Goods", uom="Units", initial_stock=0)
        db.add_all([self.prod_rod, self.prod_chair])
        db.commit()

        self.wh_a_id = self.wh_a.id
        self.wh_b_id = self.wh_b.id
        self.loc_a1_id = self.loc_a1.id
        self.loc_a2_id = self.loc_a2.id
        self.loc_b1_id = self.loc_b1.id
        self.prod_rod_id = self.prod_rod.id
        self.prod_chair_id = self.prod_chair.id
        db.close()

    # -------------------------------------------------------------------------
    # 1. RECEIPTS WORKFLOW TESTS
    # -------------------------------------------------------------------------
    def test_create_and_validate_receipt(self):
        """
        RECEIPT EXAMPLE:
        Receive 50 Steel Rods
        Before: 100 (we start with 100)
        After validation: 150
        """
        db = TestingSessionLocal()
        initial_stock = Stock(product_id=self.prod_rod_id, warehouse_id=self.wh_a_id, location_id=self.loc_a1_id, quantity=100.0)
        db.add(initial_stock)
        db.commit()
        db.close()

        # 1. Create Receipt
        payload = {
            "supplier": "Acme Steel Corp",
            "warehouse_id": self.wh_a_id,
            "location_id": self.loc_a1_id,
            "items": [
                {"product_id": self.prod_rod_id, "quantity": 50.0}
            ]
        }
        res = self.client.post("/receipts", json=payload)
        self.assertEqual(res.status_code, 201)
        receipt = res.json()
        self.assertEqual(receipt["status"], "Draft")
        self.assertEqual(receipt["supplier"], "Acme Steel Corp")
        self.assertEqual(len(receipt["items"]), 1)
        receipt_id = receipt["id"]

        # Stock before validation must still be 100
        db = TestingSessionLocal()
        s_before = db.query(Stock).filter_by(product_id=self.prod_rod_id, location_id=self.loc_a1_id).first()
        self.assertEqual(s_before.quantity, 100.0)
        db.close()

        # 2. Validate Receipt
        val_res = self.client.post(f"/receipts/{receipt_id}/validate")
        self.assertEqual(val_res.status_code, 200)
        self.assertEqual(val_res.json()["status"], "Done")

        # 3. Stock after validation must be 150
        db = TestingSessionLocal()
        s_after = db.query(Stock).filter_by(product_id=self.prod_rod_id, location_id=self.loc_a1_id).first()
        self.assertEqual(s_after.quantity, 150.0)

        # 4. Movement ledger entry verification
        movement = db.query(StockMovement).filter_by(reference_id=receipt_id, movement_type="RECEIPT").first()
        self.assertIsNotNone(movement)
        self.assertEqual(movement.product_id, self.prod_rod_id)
        self.assertEqual(movement.quantity, 50.0)
        self.assertEqual(movement.destination_location_id, self.loc_a1_id)
        self.assertIsNone(movement.source_location_id)
        self.assertIsNotNone(movement.timestamp)
        db.close()

    def test_receipt_items_crud(self):
        # Create empty draft receipt
        payload = {
            "supplier": "Global Supplies",
            "warehouse_id": self.wh_a_id,
            "location_id": self.loc_a1_id,
            "items": []
        }
        res = self.client.post("/receipts", json=payload)
        receipt_id = res.json()["id"]

        # Add item
        item_res = self.client.post(f"/receipts/{receipt_id}/items", json={"product_id": self.prod_chair_id, "quantity": 10.0})
        self.assertEqual(item_res.status_code, 201)
        item_id = item_res.json()["id"]

        # List items
        items_res = self.client.get(f"/receipts/{receipt_id}/items")
        self.assertEqual(items_res.status_code, 200)
        self.assertEqual(len(items_res.json()), 1)

        # Delete item
        del_res = self.client.delete(f"/receipts/{receipt_id}/items/{item_id}")
        self.assertEqual(del_res.status_code, 204)

        # Ensure validation fails with no items
        val_fail = self.client.post(f"/receipts/{receipt_id}/validate")
        self.assertEqual(val_fail.status_code, 400)

    def test_receipt_negative_quantity_and_invalid_location(self):
        # Negative quantity rejected
        payload = {
            "supplier": "Bad Vendor",
            "warehouse_id": self.wh_a_id,
            "location_id": self.loc_a1_id,
            "items": [{"product_id": self.prod_rod_id, "quantity": -5.0}]
        }
        res = self.client.post("/receipts", json=payload)
        self.assertEqual(res.status_code, 422)

        # Location not belonging to warehouse rejected
        payload2 = {
            "supplier": "Vendor",
            "warehouse_id": self.wh_a_id,
            "location_id": self.loc_b1_id,  # belongs to wh_b
            "items": [{"product_id": self.prod_rod_id, "quantity": 10.0}]
        }
        res2 = self.client.post("/receipts", json=payload2)
        self.assertEqual(res2.status_code, 400)

    # -------------------------------------------------------------------------
    # 2. DELIVERIES WORKFLOW TESTS
    # -------------------------------------------------------------------------
    def test_create_and_validate_delivery_lifecycle(self):
        """
        DELIVERY EXAMPLE:
        Deliver 10 chairs
        Before: 50
        Pick -> Pack -> Validate
        After validation: 40
        """
        db = TestingSessionLocal()
        initial_stock = Stock(product_id=self.prod_chair_id, warehouse_id=self.wh_a_id, location_id=self.loc_a1_id, quantity=50.0)
        db.add(initial_stock)
        db.commit()
        db.close()

        # 1. Create delivery (Draft)
        payload = {
            "customer_reference": "SO-2026-001",
            "warehouse_id": self.wh_a_id,
            "location_id": self.loc_a1_id,
            "items": [{"product_id": self.prod_chair_id, "quantity": 10.0}]
        }
        res = self.client.post("/deliveries", json=payload)
        self.assertEqual(res.status_code, 201)
        delivery_id = res.json()["id"]
        self.assertEqual(res.json()["status"], "Draft")

        # 2. Cannot validate before packing
        val_early = self.client.post(f"/deliveries/{delivery_id}/validate")
        self.assertEqual(val_early.status_code, 400)

        # 3. Pick: Draft -> Waiting
        pick_res = self.client.post(f"/deliveries/{delivery_id}/pick")
        self.assertEqual(pick_res.status_code, 200)
        self.assertEqual(pick_res.json()["status"], "Waiting")

        # 4. Pack: Waiting -> Ready
        pack_res = self.client.post(f"/deliveries/{delivery_id}/pack")
        self.assertEqual(pack_res.status_code, 200)
        self.assertEqual(pack_res.json()["status"], "Ready")

        # 5. Validate: Ready -> Done
        val_res = self.client.post(f"/deliveries/{delivery_id}/validate")
        self.assertEqual(val_res.status_code, 200)
        self.assertEqual(val_res.json()["status"], "Done")

        # 6. Verify stock decreased from 50 to 40
        db = TestingSessionLocal()
        s_after = db.query(Stock).filter_by(product_id=self.prod_chair_id, location_id=self.loc_a1_id).first()
        self.assertEqual(s_after.quantity, 40.0)

        # 7. Verify stock movement
        movement = db.query(StockMovement).filter_by(reference_id=delivery_id, movement_type="DELIVERY").first()
        self.assertIsNotNone(movement)
        self.assertEqual(movement.product_id, self.prod_chair_id)
        self.assertEqual(movement.quantity, 10.0)
        self.assertEqual(movement.source_location_id, self.loc_a1_id)
        self.assertIsNone(movement.destination_location_id)
        self.assertIsNotNone(movement.timestamp)
        db.close()

    def test_delivery_insufficient_stock_prevented(self):
        # Case 1: No stock record at all
        payload = {
            "customer_reference": "SO-FAIL-1",
            "warehouse_id": self.wh_a_id,
            "location_id": self.loc_a1_id,
            "items": [{"product_id": self.prod_rod_id, "quantity": 100.0}]
        }
        res = self.client.post("/deliveries", json=payload)
        del_id = res.json()["id"]

        self.client.post(f"/deliveries/{del_id}/pick")
        self.client.post(f"/deliveries/{del_id}/pack")
        val_res = self.client.post(f"/deliveries/{del_id}/validate")
        self.assertEqual(val_res.status_code, 400)
        self.assertIn("No stock found", val_res.json()["detail"])

        # Case 2: Stock exists (e.g. 5 units) but delivery requests 10 units
        db = TestingSessionLocal()
        s = Stock(product_id=self.prod_rod_id, warehouse_id=self.wh_a_id, location_id=self.loc_a1_id, quantity=5.0)
        db.add(s)
        db.commit()
        db.close()

        payload2 = {
            "customer_reference": "SO-FAIL-2",
            "warehouse_id": self.wh_a_id,
            "location_id": self.loc_a1_id,
            "items": [{"product_id": self.prod_rod_id, "quantity": 10.0}]
        }
        res2 = self.client.post("/deliveries", json=payload2)
        del_id2 = res2.json()["id"]

        self.client.post(f"/deliveries/{del_id2}/pick")
        self.client.post(f"/deliveries/{del_id2}/pack")
        val_res2 = self.client.post(f"/deliveries/{del_id2}/validate")
        self.assertEqual(val_res2.status_code, 400)
        self.assertIn("Insufficient stock", val_res2.json()["detail"])

    # -------------------------------------------------------------------------
    # 3. INTERNAL TRANSFERS WORKFLOW TESTS
    # -------------------------------------------------------------------------
    def test_internal_transfer_lifecycle_and_company_stock_invariant(self):
        """
        INTERNAL TRANSFER EXAMPLE:
        Warehouse A: 100
        Transfer 20 to Warehouse B
        After:
        Warehouse A: 80
        Warehouse B: 20
        Total company stock remains 100!
        """
        db = TestingSessionLocal()
        initial_stock = Stock(product_id=self.prod_rod_id, warehouse_id=self.wh_a_id, location_id=self.loc_a1_id, quantity=100.0)
        db.add(initial_stock)
        db.commit()
        db.close()

        # 1. Create transfer
        payload = {
            "source_warehouse_id": self.wh_a_id,
            "source_location_id": self.loc_a1_id,
            "destination_warehouse_id": self.wh_b_id,
            "destination_location_id": self.loc_b1_id,
            "items": [{"product_id": self.prod_rod_id, "quantity": 20.0}]
        }
        res = self.client.post("/transfers", json=payload)
        self.assertEqual(res.status_code, 201)
        transfer_id = res.json()["id"]
        self.assertEqual(res.json()["status"], "Draft")

        # 2. Validate transfer
        val_res = self.client.post(f"/transfers/{transfer_id}/validate")
        self.assertEqual(val_res.status_code, 200)
        self.assertEqual(val_res.json()["status"], "Done")

        # 3. Verify stock quantities:
        # Warehouse A (loc_a1) = 80
        # Warehouse B (loc_b1) = 20
        # Total = 100
        db = TestingSessionLocal()
        s_source = db.query(Stock).filter_by(product_id=self.prod_rod_id, location_id=self.loc_a1_id).first()
        s_dest = db.query(Stock).filter_by(product_id=self.prod_rod_id, location_id=self.loc_b1_id).first()
        self.assertEqual(s_source.quantity, 80.0)
        self.assertEqual(s_dest.quantity, 20.0)

        # Total company stock invariant:
        total_stock = sum(s.quantity for s in db.query(Stock).filter_by(product_id=self.prod_rod_id).all())
        self.assertEqual(total_stock, 100.0)

        # 4. Movement ledger entry verification
        movement = db.query(StockMovement).filter_by(reference_id=transfer_id, movement_type="INTERNAL_TRANSFER").first()
        self.assertIsNotNone(movement)
        self.assertEqual(movement.product_id, self.prod_rod_id)
        self.assertEqual(movement.quantity, 20.0)
        self.assertEqual(movement.source_location_id, self.loc_a1_id)
        self.assertEqual(movement.destination_location_id, self.loc_b1_id)
        self.assertIsNotNone(movement.timestamp)
        db.close()

    def test_transfer_same_source_and_destination_prevented(self):
        payload = {
            "source_warehouse_id": self.wh_a_id,
            "source_location_id": self.loc_a1_id,
            "destination_warehouse_id": self.wh_a_id,
            "destination_location_id": self.loc_a1_id,
            "items": [{"product_id": self.prod_rod_id, "quantity": 10.0}]
        }
        res = self.client.post("/transfers", json=payload)
        self.assertEqual(res.status_code, 400)
        self.assertIn("Source and destination cannot be the same", res.json()["detail"])

    def test_transfer_insufficient_stock_prevented(self):
        payload = {
            "source_warehouse_id": self.wh_a_id,
            "source_location_id": self.loc_a1_id,
            "destination_warehouse_id": self.wh_b_id,
            "destination_location_id": self.loc_b1_id,
            "items": [{"product_id": self.prod_rod_id, "quantity": 999.0}]
        }
        res = self.client.post("/transfers", json=payload)
        t_id = res.json()["id"]

        val_res = self.client.post(f"/transfers/{t_id}/validate")
        self.assertEqual(val_res.status_code, 400)

    # -------------------------------------------------------------------------
    # 4. STOCK MOVEMENT HISTORY TESTS
    # -------------------------------------------------------------------------
    def test_stock_movement_history_and_filtering(self):
        # Create stock via receipt
        r_res = self.client.post("/receipts", json={
            "supplier": "Vendor 1",
            "warehouse_id": self.wh_a_id,
            "location_id": self.loc_a1_id,
            "items": [{"product_id": self.prod_rod_id, "quantity": 100.0}]
        })
        self.client.post(f"/receipts/{r_res.json()['id']}/validate")

        # Deliver some stock
        d_res = self.client.post("/deliveries", json={
            "customer_reference": "Cust 1",
            "warehouse_id": self.wh_a_id,
            "location_id": self.loc_a1_id,
            "items": [{"product_id": self.prod_rod_id, "quantity": 25.0}]
        })
        del_id = d_res.json()["id"]
        self.client.post(f"/deliveries/{del_id}/pick")
        self.client.post(f"/deliveries/{del_id}/pack")
        self.client.post(f"/deliveries/{del_id}/validate")

        # Transfer some stock
        t_res = self.client.post("/transfers", json={
            "source_warehouse_id": self.wh_a_id,
            "source_location_id": self.loc_a1_id,
            "destination_warehouse_id": self.wh_b_id,
            "destination_location_id": self.loc_b1_id,
            "items": [{"product_id": self.prod_rod_id, "quantity": 15.0}]
        })
        self.client.post(f"/transfers/{t_res.json()['id']}/validate")

        # 1. Fetch all movements
        mov_res = self.client.get("/stock-movements")
        self.assertEqual(mov_res.status_code, 200)
        movements = mov_res.json()
        self.assertEqual(len(movements), 3)

        # 2. Filter by movement_type
        r_filter = self.client.get("/stock-movements?movement_type=RECEIPT")
        self.assertEqual(len(r_filter.json()), 1)
        self.assertEqual(r_filter.json()[0]["quantity"], 100.0)

        d_filter = self.client.get("/stock-movements?movement_type=DELIVERY")
        self.assertEqual(len(d_filter.json()), 1)
        self.assertEqual(d_filter.json()[0]["quantity"], 25.0)

        t_filter = self.client.get("/stock-movements?movement_type=INTERNAL_TRANSFER")
        self.assertEqual(len(t_filter.json()), 1)
        self.assertEqual(t_filter.json()[0]["quantity"], 15.0)

        # 3. Check individual movement endpoint
        mov_id = movements[0]["id"]
        single_mov = self.client.get(f"/stock-movements/{mov_id}")
        self.assertEqual(single_mov.status_code, 200)
        self.assertEqual(single_mov.json()["id"], mov_id)

    # -------------------------------------------------------------------------
    # 5. CANCELLATION & MULTI-ITEM EDGE CASE TESTS
    # -------------------------------------------------------------------------
    def test_cancellation_workflow(self):
        # 1. Receipt Cancellation
        r = self.client.post("/receipts", json={
            "supplier": "Cancel Supplier",
            "warehouse_id": self.wh_a_id,
            "location_id": self.loc_a1_id,
            "items": [{"product_id": self.prod_rod_id, "quantity": 10.0}]
        }).json()
        c_res = self.client.post(f"/receipts/{r['id']}/cancel")
        self.assertEqual(c_res.status_code, 200)
        self.assertEqual(c_res.json()["status"], "Canceled")
        # Cannot validate canceled receipt
        val_fail = self.client.post(f"/receipts/{r['id']}/validate")
        self.assertEqual(val_fail.status_code, 400)

        # 2. Delivery Cancellation
        d = self.client.post("/deliveries", json={
            "customer_reference": "Cancel Cust",
            "warehouse_id": self.wh_a_id,
            "location_id": self.loc_a1_id,
            "items": [{"product_id": self.prod_rod_id, "quantity": 10.0}]
        }).json()
        d_cancel = self.client.post(f"/deliveries/{d['id']}/cancel")
        self.assertEqual(d_cancel.status_code, 200)
        self.assertEqual(d_cancel.json()["status"], "Canceled")

        # 3. Transfer Cancellation
        t = self.client.post("/transfers", json={
            "source_warehouse_id": self.wh_a_id,
            "source_location_id": self.loc_a1_id,
            "destination_warehouse_id": self.wh_b_id,
            "destination_location_id": self.loc_b1_id,
            "items": [{"product_id": self.prod_rod_id, "quantity": 10.0}]
        }).json()
        t_cancel = self.client.post(f"/transfers/{t['id']}/cancel")
        self.assertEqual(t_cancel.status_code, 200)
        self.assertEqual(t_cancel.json()["status"], "Canceled")

    def test_multi_item_receipt_and_delivery(self):
        # 1. Multi-item receipt
        r_payload = {
            "supplier": "Multi Vendor",
            "warehouse_id": self.wh_a_id,
            "location_id": self.loc_a1_id,
            "items": [
                {"product_id": self.prod_rod_id, "quantity": 50.0},
                {"product_id": self.prod_chair_id, "quantity": 30.0}
            ]
        }
        r = self.client.post("/receipts", json=r_payload).json()
        self.client.post(f"/receipts/{r['id']}/validate")

        db = TestingSessionLocal()
        s_rod = db.query(Stock).filter_by(product_id=self.prod_rod_id, location_id=self.loc_a1_id).first()
        s_chair = db.query(Stock).filter_by(product_id=self.prod_chair_id, location_id=self.loc_a1_id).first()
        self.assertEqual(s_rod.quantity, 50.0)
        self.assertEqual(s_chair.quantity, 30.0)
        db.close()

        # 2. Multi-item delivery
        d_payload = {
            "customer_reference": "Multi-Order-001",
            "warehouse_id": self.wh_a_id,
            "location_id": self.loc_a1_id,
            "items": [
                {"product_id": self.prod_rod_id, "quantity": 20.0},
                {"product_id": self.prod_chair_id, "quantity": 10.0}
            ]
        }
        d = self.client.post("/deliveries", json=d_payload).json()
        self.client.post(f"/deliveries/{d['id']}/pick")
        self.client.post(f"/deliveries/{d['id']}/pack")
        self.client.post(f"/deliveries/{d['id']}/validate")

        db = TestingSessionLocal()
        s_rod_after = db.query(Stock).filter_by(product_id=self.prod_rod_id, location_id=self.loc_a1_id).first()
        s_chair_after = db.query(Stock).filter_by(product_id=self.prod_chair_id, location_id=self.loc_a1_id).first()
        self.assertEqual(s_rod_after.quantity, 30.0)
        self.assertEqual(s_chair_after.quantity, 20.0)
        db.close()


if __name__ == "__main__":
    unittest.main()
