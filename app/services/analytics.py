from __future__ import annotations
from collections import Counter, defaultdict
from typing import Dict, List, Optional, Tuple
from app.models import Order, EnrichedOrder
from app.utils import parse_dt

PRIO = {
    "COD_HIGH_VALUE": 1,
    "MULTI_FAILED_PAYMENTS": 1,
    "ADDR_CHANGED_AFTER_PAY": 1,
    "RETURN_WITHIN_24H": 1,
}

def enrich_order(o: Order) -> EnrichedOrder:
    order_value = sum(i.qty * i.unit_price for i in o.items)
    discount_total = max(0, int(o.pricing.discount or 0))
    tax_total = max(0, int(o.pricing.tax or 0))
    net_payable = order_value - discount_total + tax_total

    paid_amount = sum(p.amount for p in o.payments if p.status == "success")
    refunded_amount = sum(p.amount for p in o.payments if p.status == "refunded")

    # payment_status
    if refunded_amount >= net_payable and net_payable > 0:
        payment_status = "refunded"
    elif paid_amount >= net_payable and net_payable > 0:
        payment_status = "paid"
    elif paid_amount > 0:
        payment_status = "partial"
    else:
        # COD pending treated separately
        if any(p.method == "COD" for p in o.payments):
            payment_status = "cod_pending"
        else:
            payment_status = "unpaid"

    # fulfillment_status from latest shipment/event
    fulfillment_status = "pending"
    if o.shipments:
        # check any returned
        if any(s.status == "returned" for s in o.shipments):
            fulfillment_status = "returned"
        elif any(s.status == "delivered" for s in o.shipments):
            fulfillment_status = "delivered"
        elif any(s.status == "shipped" for s in o.shipments):
            fulfillment_status = "shipped"

    # delivery TAT
    shipped_at = None
    delivered_at = None
    for s in o.shipments:
        if s.shipped_at and not shipped_at:
            shipped_at = parse_dt(s.shipped_at)
        if s.delivered_at:
            delivered_at = parse_dt(s.delivered_at)
    delivery_tat_hours = None
    if shipped_at and delivered_at:
        delivery_tat_hours = (delivered_at - shipped_at).total_seconds()/3600

    # risk flags
    risk_flags: List[str] = []
    is_cod = any(p.method == "COD" for p in o.payments)
    if is_cod and net_payable >= 5000:
        risk_flags.append("COD_HIGH_VALUE")

    failed_payments = sum(1 for p in o.payments if p.status == "failed")
    if failed_payments >= 2:
        risk_flags.append("MULTI_FAILED_PAYMENTS")

    # Address changed after pay
    paid_time = None
    for ev in o.events:
        if ev.type == "paid":
            paid_time = parse_dt(ev.time)
            break
    if paid_time:
        for ev in o.events:
            if ev.type == "address_changed":
                t = parse_dt(ev.time)
                if t and t > paid_time:
                    risk_flags.append("ADDR_CHANGED_AFTER_PAY")
                    break

    # Return within 24h of delivery
    delivered_time = None
    returned_time = None
    for ev in o.events:
        if ev.type == "delivered" and not delivered_time:
            delivered_time = parse_dt(ev.time)
        if ev.type == "returned" and not returned_time:
            returned_time = parse_dt(ev.time)
    if delivered_time and returned_time:
        if (returned_time - delivered_time).total_seconds() <= 24*3600:
            risk_flags.append("RETURN_WITHIN_24H")

    return EnrichedOrder(
        order_id=o.order_id,
        created_at=o.created_at,
        customer=o.customer,
        items=o.items,
        order_value=order_value,
        discount_total=discount_total,
        tax_total=tax_total,
        net_payable=net_payable,
        paid_amount=paid_amount,
        payment_status=payment_status,
        fulfillment_status=fulfillment_status,
        delivery_tat_hours=delivery_tat_hours,
        risk_flags=risk_flags
    )

def summary(enriched: List[EnrichedOrder]) -> Dict:
    total = len(enriched)
    gmv = sum(o.order_value for o in enriched)
    net = sum(o.net_payable for o in enriched)
    pay_counts = Counter(o.payment_status for o in enriched)
    fulf_counts = Counter(o.fulfillment_status for o in enriched)

    # avg delivery tat (delivered only)
    tss = [o.delivery_tat_hours for o in enriched if o.delivery_tat_hours is not None]
    avg_tat = sum(tss)/len(tss) if tss else None

    sku_rev = Counter()
    city_gmv = Counter()
    for o in enriched:
        city = o.customer.city or "unknown"
        city_gmv[city] += o.net_payable
        for it in o.items:
            sku_rev[it.sku] += it.qty * it.unit_price

    return {
        "total_orders": total,
        "gmv": gmv,
        "net_revenue": net,
        "payment_status_counts": dict(pay_counts),
        "fulfillment_status_counts": dict(fulf_counts),
        "avg_delivery_tat_hours": round(avg_tat, 2) if avg_tat is not None else None,
        "top_skus_by_revenue": sku_rev.most_common(5),
        "top_cities_by_gmv": city_gmv.most_common(5),
    }

def funnel(enriched: List[EnrichedOrder]) -> Dict:
    # based on events inferred from statuses
    created = len(enriched)
    paid = sum(1 for o in enriched if o.payment_status in ("paid","partial","refunded"))
    shipped = sum(1 for o in enriched if o.fulfillment_status in ("shipped","delivered","returned"))
    delivered = sum(1 for o in enriched if o.fulfillment_status in ("delivered","returned"))
    returned = sum(1 for o in enriched if o.fulfillment_status == "returned")
    return {"created": created, "paid": paid, "shipped": shipped, "delivered": delivered, "returned": returned}

def alerts(enriched: List[EnrichedOrder], min_risk: int = 2) -> List[EnrichedOrder]:
    def severity(o: EnrichedOrder) -> int:
        return len(o.risk_flags)
    res = [o for o in enriched if len(o.risk_flags) >= min_risk]
    res.sort(key=severity, reverse=True)
    return res
