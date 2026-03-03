# E-Commerce Orders Intelligence API

![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-009688.svg?logo=fastapi)
![Pydantic](https://img.shields.io/badge/Pydantic-2.8.2-e92063.svg)
![Pytest](https://img.shields.io/badge/Tests-Pytest-yellow.svg)
## Overview
A robust, high-performance FastAPI backend service designed to parse, enrich, manage, and analyze e-commerce order data. Built with resilience in mind, this API handles messy, real-world JSON data—smoothly skipping and isolating bad or corrupt records—while keeping the application stable.

## Key Features
- **Full CRUD Orders Management**: Create, Read, Update, and Delete individual orders seamlessly.
- **Advanced Search & Filtering**: Paginated order retrieval with filtering capabilities by status, payment state, city, customer tier, and order value.
- **Resilient Data Ingestion**: Automatically handles missing fields, invalid date formats, duplicate IDs, and placeholder values (like `???`) without crashing.
- **Data Enrichment**: Built-in logic to evaluate and append risk scores, standardizing inconsistent order metrics.
- **Analytics Engine**: Real-time analytical endpoints providing summary statistics, conversion funnels, and high-risk alerts.
- **Interactive API Docs**: Auto-generated OpenAPI (Swagger) interface for easy testing and integration.

## Tech Stack
- **Framework:** FastAPI
- **Validation:** Pydantic (v2)
- **Server:** Uvicorn
- **Testing:** Pytest / Pytest-asyncio

---

## Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd fastapi_orders_case
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv .venv
   
   # Windows:
   .venv\Scripts\activate
   
   # macOS/Linux:
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the API server:**
   ```bash
   uvicorn app.main:app --reload
   ```

5. **View API Documentation:**
   Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) in your browser.

---

## API Endpoints

### System
- `GET /health` – Returns API operational status, along with metrics on successfully loaded vs. bad records.

### Orders
- `GET /orders` – Fetch all orders with optional pagination and filters (`status`, `payment_status`, `city`, `customer_tier`, `min_value`, `max_value`).
- `GET /orders/{order_id}` – Fetch details of a specific order.
- `POST /orders` – Create a new order.
- `PUT /orders/{order_id}` – Update an existing order.
- `DELETE /orders/{order_id}` – Delete an order.

### Analytics
- `GET /analytics/summary` – Summary statistics for sales, refunds, etc.
- `GET /analytics/funnel` – Breakdown of the fulfillment and payment status funnel.
- `GET /analytics/alerts` – Get a list of high-risk flagged orders (filter by `min_risk` query param, default is 2).

---

## Testing

To run the full test suite (Models, Routes, and Analytics):
```bash
pytest
```

## Data Management
On startup, the API loads the seed data from `data/orders.json`. Records failing strict schema validation or identified as duplicates are safely bypassed and reported to the application state logs without disrupting API functionality. Outputs (such as custom data exports) can be naturally extended into the `/outputs` directory.
