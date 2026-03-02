from __future__ import annotations
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.state import STATE

router = APIRouter(tags=["orders"])

@router.get("/orders/{order_id}")
def get_order(order_id: str):
    o = STATE["enriched_by_id"].get(order_id)
    if not o:
        raise HTTPException(status_code=404, detail="order not found")
    return o

@router.get("/orders")
def search_orders(
    status: Optional[str] = Query(default=None, description="fulfillment status: pending/shipped/delivered/returned"),
    payment_status: Optional[str] = Query(default=None, description="paid/partial/unpaid/refunded/cod_pending"),
    city: Optional[str] = None,
    customer_tier: Optional[str] = None,
    min_value: Optional[int] = Query(default=None, ge=0),
    max_value: Optional[int] = Query(default=None, ge=0),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
):
    rows = STATE["enriched"]
    if status:
        rows = [o for o in rows if o["fulfillment_status"] == status]
    if payment_status:
        rows = [o for o in rows if o["payment_status"] == payment_status]
    if city:
        rows = [o for o in rows if (o["customer"].get("city") or "").lower() == city.lower()]
    if customer_tier:
        rows = [o for o in rows if (o["customer"].get("tier") or "").lower() == customer_tier.lower()]
    if min_value is not None:
        rows = [o for o in rows if o["net_payable"] >= min_value]
    if max_value is not None:
        rows = [o for o in rows if o["net_payable"] <= max_value]

    total = len(rows)
    start = (page-1)*page_size
    end = start + page_size
    return {"total": total, "page": page, "page_size": page_size, "results": rows[start:end]}
