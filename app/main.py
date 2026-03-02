from __future__ import annotations
import logging
from pathlib import Path
from fastapi import FastAPI
from app.routes.orders import router as orders_router
from app.routes.analytics import router as analytics_router
from app.services.parser import load_orders_json, parse_orders
from app.services.analytics import enrich_order
from app.state import STATE

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("orders_case")

def create_app() -> FastAPI:
    app = FastAPI(title="E-commerce Orders Intelligence API", version="1.0")

    @app.on_event("startup")
    def _load_data():
        data_path = Path(__file__).resolve().parent.parent / "data" / "orders.json"
        payload = load_orders_json(data_path)
        orders, bad = parse_orders(payload)
        STATE["orders"] = orders
        STATE["bad_records"] = bad

        enriched_models = [enrich_order(o) for o in orders]
        STATE["enriched_models"] = enriched_models
        STATE["enriched"] = [o.model_dump() for o in enriched_models]
        STATE["enriched_by_id"] = {o.order_id: o.model_dump() for o in enriched_models}

        log.info("Loaded %d orders (%d bad)", len(orders), len(bad))

    @app.get("/health", tags=["health"])
    def health():
        return {"status": "ok", "orders_loaded": len(STATE["orders"]), "bad_records": len(STATE["bad_records"])}

    app.include_router(orders_router)
    app.include_router(analytics_router)
    return app

app = create_app()
