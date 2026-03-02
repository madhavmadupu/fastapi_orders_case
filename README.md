# FastAPI Interview Case: E-commerce Orders Intelligence API (Single JSON)

## What you get
- `data/orders.json` (single nested JSON with 500 orders; some are intentionally messy)
- A working FastAPI skeleton under `app/`

## Goal
Create an API that parses and enriches orders and serves analytics.

## Run
```bash
python -m venv .venv
source .venv/bin/activate  # (Windows: .venv\Scripts\activate)
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open:
- http://127.0.0.1:8000/docs

## Endpoints included
- GET /health
- GET /orders/{order_id}
- GET /orders (filters + pagination)
- GET /analytics/summary
- GET /analytics/funnel
- GET /analytics/alerts?min_risk=2

## Notes
- Some orders have invalid dates, missing fields, duplicate IDs, or '???' values.
- App must not crash; skip bad records and continue.
- Candidates can extend enrichment logic, add exports to `outputs/`, add tests, etc.
