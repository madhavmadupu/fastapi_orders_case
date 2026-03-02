import pytest
from app.models import Order, EnrichedOrder
from app.services.analytics import enrich_order, summary, funnel

def test_enrich_adds_payment_mismatch_risk():
    payload = {
        "order_id": "ORD-123",
        "customer": {"customer_id": "C-1", "name": "Test"},
        "items": [{"sku": "SKU-1", "name": "A", "qty": 1, "unit_price": 500}], # order_value 500
        "pricing": {"discount": 0, "tax": 50, "currency": "INR"}, # net_payable 550
        "payments": [{"method": "card", "status": "success", "amount": 500, "time": "2026-02-01T00:00:00"}], # paid 500, mismatch!
        "events": [],
        "shipments": []
    }
    o = Order.model_validate(payload)
    enriched = enrich_order(o)
    assert "PAYMENT_AMOUNT_MISMATCH" in enriched.risk_flags

def test_funnel():
    # Write a test that validates the funnel numbers
    o1 = Order.model_validate({"order_id": "1", "customer": {"customer_id": "C-1", "name": "A"}}) # Created
    
    o2 = Order.model_validate({
        "order_id": "2", "customer": {"customer_id": "C-1", "name": "A"},
        "items": [{"sku": "S", "name": "A", "qty": 1, "unit_price": 100}],
        "payments": [{"method": "card", "status": "success", "amount": 100, "time": "2026-02-01T00:00:00"}]
    }) # Paid
    
    o3 = Order.model_validate({
        "order_id": "3", "customer": {"customer_id": "C-1", "name": "A"},
        "items": [{"sku": "S", "name": "A", "qty": 1, "unit_price": 100}],
        "payments": [{"method": "card", "status": "success", "amount": 100, "time": "2026-02-01T00:00:00"}],
        "shipments": [{"carrier": "fedex", "status": "shipped"}]
    }) # Shipped
    
    enriched = [enrich_order(o) for o in [o1, o2, o3]]
    res = funnel(enriched)
    assert res["created"] == 3
    assert res["paid"] == 2
    assert res["shipped"] == 1
    assert res["delivered"] == 0

def test_marketing_efficacy_in_summary():
    o1 = Order.model_validate({
        "order_id": "1", "customer": {"customer_id": "C-1", "name": "A"},
        "items": [{"sku": "S", "name": "A", "qty": 1, "unit_price": 100}],
        "meta": {"channel": "app", "coupon": "VIP20"}
    })
    
    enriched = [enrich_order(o1)]
    res = summary(enriched)
    assert "marketing_efficacy" in res
    assert res["marketing_efficacy"]["by_channel"]["app"]["gmv"] == 100
    assert res["marketing_efficacy"]["by_coupon"]["VIP20"]["uses"] == 1
