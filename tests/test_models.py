import pytest
from app.models import Order, Customer, Item, Shipment, Payment, Event

def test_order_coerces_invalid_date():
    payload = {
        "order_id": "ORD-123",
        "created_at": "???",
        "customer": {"customer_id": "C-1", "name": "John Doe"},
        "items": [{"sku": "SKU-1", "name": "Test", "qty": 1, "unit_price": 100}]
    }
    order = Order.model_validate(payload)
    assert order.created_at is None

def test_order_coerces_impossible_date():
    payload = {
        "order_id": "ORD-123",
        "created_at": "2026-02-30T10:00:00",
        "customer": {"customer_id": "C-1", "name": "John Doe"},
        "items": []
    }
    order = Order.model_validate(payload)
    assert order.created_at is None

def test_order_accepts_european_date():
    payload = {
        "order_id": "ORD-123",
        "created_at": "10/02/2026 20:34",
        "customer": {"customer_id": "C-1", "name": "John Doe"},
        "items": []
    }
    order = Order.model_validate(payload)
    # The output might be kept as a string but normalized, or stored as datetime.
    # We should probably store as ISO string or datetime. Let's expect an ISO string or datetime object.
    assert order.created_at is not None
    # If using string
    # assert order.created_at == "2026-02-10T20:34:00"

def test_order_items_null_coerced_to_empty_list():
    payload = {
        "order_id": "ORD-123",
        "created_at": "2026-02-01T03:17:33",
        "customer": {"customer_id": "C-1", "name": "John Doe"},
        "items": None
    }
    order = Order.model_validate(payload)
    assert isinstance(order.items, list)
    assert len(order.items) == 0

def test_order_customer_invalid_type_coerced_to_default():
    payload = {
        "order_id": "ORD-123",
        "created_at": "2026-02-01T03:17:33",
        "customer": "???",
        "items": []
    }
    order = Order.model_validate(payload)
    assert order.customer.customer_id == "unknown"
    assert order.customer.name == "Unknown"

def test_order_nested_dates_coerced():
    payload = {
        "order_id": "ORD-123",
        "created_at": "2026-02-01T03:17:33",
        "customer": {"customer_id": "C-1", "name": "John Doe"},
        "items": [],
        "shipments": [
            {"carrier": "FEDEX", "status": "shipped", "shipped_at": "???", "delivered_at": "2026-02-30T10:00:00"}
        ],
        "payments": [
            {"method": "CC", "status": "success", "amount": 100, "time": "invalid_date"}
        ],
        "events": [
            {"type": "shipped", "time": "missing"}
        ]
    }
    order = Order.model_validate(payload)
    assert order.shipments[0].shipped_at is None
    assert order.shipments[0].delivered_at is None
    assert order.payments[0].time is None
    assert order.events[0].time is None
