from __future__ import annotations
from typing import List, Optional, Dict, Any
from app.models import Order, EnrichedOrder
from app.state import STATE
from app.services.analytics import enrich_order

class OrderRepository:
    def get_by_id(self, order_id: str) -> Optional[Dict[str, Any]]:
        return STATE["enriched_by_id"].get(order_id)

    def search(
        self,
        status: Optional[str] = None,
        payment_status: Optional[str] = None,
        city: Optional[str] = None,
        customer_tier: Optional[str] = None,
        min_value: Optional[int] = None,
        max_value: Optional[int] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> Dict[str, Any]:
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
        start = (page - 1) * page_size
        end = start + page_size
        return {"total": total, "page": page, "page_size": page_size, "results": rows[start:end]}

    def create(self, order: Order) -> Dict[str, Any]:
        # Perform enrichment
        enriched = enrich_order(order)
        dump = enriched.model_dump()
        
        # Add to state tracking explicitly 
        STATE["orders"].append(order)
        STATE["enriched_models"].append(enriched)
        STATE["enriched"].append(dump)
        STATE["enriched_by_id"][order.order_id] = dump
        
        return dump

    def update(self, order_id: str, updated_order: Order) -> Optional[Dict[str, Any]]:
        # Validate order exists
        if order_id not in STATE["enriched_by_id"]:
            return None
        
        # Remove old instance completely from memory structures
        self.delete(order_id)
        
        # Add the new instance under potentially same ID
        return self.create(updated_order)

    def delete(self, order_id: str) -> bool:
        if order_id not in STATE["enriched_by_id"]:
            return False

        STATE["orders"] = [o for o in STATE["orders"] if o.order_id != order_id]
        STATE["enriched_models"] = [o for o in STATE["enriched_models"] if o.order_id != order_id]
        STATE["enriched"] = [o for o in STATE["enriched"] if o["order_id"] != order_id]
        if order_id in STATE["enriched_by_id"]:
            del STATE["enriched_by_id"][order_id]
        
        return True

def get_order_repository() -> OrderRepository:
    return OrderRepository()
