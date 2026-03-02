from __future__ import annotations
import json, logging
from pathlib import Path
from typing import Any, Dict, List, Tuple
from pydantic import ValidationError
from app.models import Order

log = logging.getLogger("orders_case")

def load_orders_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))

def parse_orders(payload: Dict[str, Any]) -> Tuple[List[Order], List[dict]]:
    good: List[Order] = []
    bad: List[dict] = []
    orders = payload.get("orders", [])
    seen = set()

    for raw in orders:
        try:
            if not isinstance(raw, dict):
                raise ValueError("order is not an object")
            oid = raw.get("order_id")
            if oid in seen:
                raise ValueError("duplicate order_id")
            order = Order.model_validate(raw)
            seen.add(order.order_id)
            good.append(order)
        except (ValidationError, Exception) as e:
            bad.append({"error": str(e), "raw": raw})
    return good, bad
