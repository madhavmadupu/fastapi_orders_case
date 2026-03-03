import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.state import STATE

client = TestClient(app)

@pytest.fixture(autouse=True)
def wipe_state():
    """Wipe the global STATE before every test to ensure isolation."""
    STATE["orders"] = []
    STATE["bad_records"] = []
    STATE["enriched_models"] = []
    STATE["enriched"] = []
    STATE["enriched_by_id"] = {}
    yield
    STATE["orders"] = []
    STATE["bad_records"] = []
    STATE["enriched_models"] = []
    STATE["enriched"] = []
    STATE["enriched_by_id"] = {}

def test_create_order_success():
    payload = {
        "order_id": "ORD-NEW-1",
        "created_at": "2026-02-01T03:17:33",
        "customer": {"customer_id": "C-1", "name": "John"},
        "items": [{"sku": "SKU-1", "name": "A", "qty": 1, "unit_price": 100}],
        "pricing": {"discount": 0, "tax": 0, "currency": "INR"},
        "payments": [],
        "shipments": [],
        "events": [],
        "meta": {}
    }
    
    response = client.post("/orders", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["order_id"] == "ORD-NEW-1"
    assert data["order_value"] == 100

def test_create_order_duplicate():
    payload = {
        "order_id": "ORD-NEW-1",
        "customer": {"customer_id": "C-1", "name": "John"}
    }
    # Create first
    client.post("/orders", json=payload)
    # Attempt to create again
    response = client.post("/orders", json=payload)
    assert response.status_code == 409

def test_get_order():
    payload = {
        "order_id": "ORD-NEW-1",
        "customer": {"customer_id": "C-1", "name": "John"}
    }
    client.post("/orders", json=payload)
    
    response = client.get("/orders/ORD-NEW-1")
    assert response.status_code == 200
    assert response.json()["order_id"] == "ORD-NEW-1"

def test_get_order_not_found():
    response = client.get("/orders/INVALID-ID")
    assert response.status_code == 404

def test_search_orders():
    client.post("/orders", json={"order_id": "ORD-1", "customer": {"customer_id": "C", "name": "A"}})
    client.post("/orders", json={"order_id": "ORD-2", "customer": {"customer_id": "C", "name": "A"}})
    
    response = client.get("/orders")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["results"]) == 2

def test_update_order_success():
    payload = {"order_id": "ORD-UPDATE-1", "customer": {"customer_id": "C-1", "name": "John"}}
    client.post("/orders", json=payload)
    
    update_payload = {"order_id": "ORD-UPDATE-1", "customer": {"customer_id": "C-2", "name": "Jane"}}
    response = client.put("/orders/ORD-UPDATE-1", json=update_payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["customer"]["name"] == "Jane"
    assert data["customer"]["customer_id"] == "C-2"

def test_update_order_id_mismatch():
    update_payload = {"order_id": "ORD-WRONG-1", "customer": {"customer_id": "C-2", "name": "Jane"}}
    response = client.put("/orders/ORD-UPDATE-1", json=update_payload)
    assert response.status_code == 400

def test_update_order_not_found():
    payload = {"order_id": "ORD-UNKNOWN", "customer": {"customer_id": "C-1", "name": "John"}}
    response = client.put("/orders/ORD-UNKNOWN", json=payload)
    assert response.status_code == 404

def test_delete_order():
    payload = {"order_id": "ORD-DEL-1", "customer": {"customer_id": "C-1", "name": "John"}}
    client.post("/orders", json=payload)
    
    response = client.delete("/orders/ORD-DEL-1")
    assert response.status_code == 204
    
    # Verify it's gone
    resp = client.get("/orders/ORD-DEL-1")
    assert resp.status_code == 404

def test_delete_order_not_found():
    response = client.delete("/orders/INVALID-DEL-1")
    assert response.status_code == 404
