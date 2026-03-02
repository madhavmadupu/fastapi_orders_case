from __future__ import annotations
from fastapi import APIRouter, Query
from app.state import STATE
from app.services.analytics import summary as summary_fn, funnel as funnel_fn, alerts as alerts_fn

router = APIRouter(tags=["analytics"])

@router.get("/analytics/summary")
def summary():
    return summary_fn(STATE["enriched_models"])

@router.get("/analytics/funnel")
def funnel():
    return funnel_fn(STATE["enriched_models"])

@router.get("/analytics/alerts")
def alerts(min_risk: int = Query(default=2, ge=1, le=4)):
    res = alerts_fn(STATE["enriched_models"], min_risk=min_risk)
    # return as dicts
    return {"count": len(res), "results": [o.model_dump() for o in res]}
