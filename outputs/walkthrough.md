# FastAPI E-Commerce Orders Intelligence API - Walkthrough

Welcome to the walkthrough of the FastAPI Orders Case implementation. This document explains the problem, the architectural decisions, and the steps taken to fulfill the requirements of parsing, cleaning, and analyzing a highly anomalous e-commerce dataset.

## Table of Contents
1. [Understanding the Problem Statement](#understanding-the-problem-statement)
2. [Architectural Setup & Dependency Management](#architectural-setup--dependency-management)
3. [Building Data Resilience (`models.py` & `parser.py`)](#building-data-resilience)
4. [Advanced Analytics & Marketing Efficacy (`analytics.py`)](#advanced-analytics--marketing-efficacy)
5. [Testing & Verification](#testing--verification)

---

## 1. Understanding the Problem Statement

The goal of this project was to establish an intelligence API over a JSON dataset of 500 e-commerce orders. The twist? The dataset is intentionally "dirty" to mimic real-world upstream bugs and legacy system errors.

**The core challenges were:**
*   Ensuring the API does not crash when hitting corrupted dates, duplicate order IDs, missing fields, or broken data types (e.g., `str` instead of `dict` for a customer).
*   Extracting meaningful business insights like total Gross Merchandise Value (GMV), return/refund rates, marketing channel efficacy, and sales funnels.
*   Enforcing strict Object-Oriented and SOLID principles throughout the clean-up and analysis code.

## 2. Architectural Setup & Dependency Management

Before touching the application code, we reviewed the `.agent/rules.md`. A strict requirement was to elevate testing to a first-class citizen. 

We installed `pytest`, `pytest-asyncio`, `httpx`, and `pydantic-settings` to ensure robust unit testing, configuration handling, and defensive scaling. They were immediately appended to `requirements.txt`.

Our project structure remains clean:
*   `app/models.py`: All Pydantic validation and type cleansing occurs here.
*   `app/services/parser.py`: Where the raw JSON is initially ingested.
*   `app/services/analytics.py`: Stores all computational logic for GMV, funnel maths, and risk flagging.
*   `app/routes/`: FastAPI API endpoints mappings.

## 3. Building Data Resilience

The defining aspect of this implementation was moving away from standard, brittle schemas to **Defensive Pydantic V2 Models**. 

In `app/models.py`, we overhauled the schemas (`Order`, `Customer`, `Item`, `Payment`, `Shipment`, `Event`) using `@field_validator(mode="before")`. 

Here is how we bypassed the edge cases:
1.  **Corrupted Dates:** Dates were failing dynamically (eg. `"2026-02-30T10:00:00"`, `"???"`, European `DD/MM/YYYY`). By running them through a strict `validate_date_string` parsing hook, any invalid or structurally impossible dates were coerced to `None` without blowing up the application.
2.  **Type Mismatches:** Sometimes the `customer` node was just the string `"???"`. A pre-validator checks if `customer` is a `dict`. If it isn't, it returns a stub `{"customer_id": "unknown", "name": "Unknown"}` safely.
3.  **Null Arrays:** If `items` came through as `null`, the validator intercepts it and returns a safe empty list `[]`. The `model_config = ConfigDict(extra="ignore")` rule ensured random unexpected keys didn't derail schema mappings either.

## 4. Advanced Analytics & Marketing Efficacy

With pristine data loaded safely in memory, we expanded `app/services/analytics.py` to deduce business logic:

1.  **GMV Verification & Risk Flags:** 
    A new risk flag `PAYMENT_AMOUNT_MISMATCH` was introduced. It validates the computed Gross Merchandise Value (`qty * unit_price - discount + tax`) against the sum of successful `payment.amount`s. If a customer paid successfully but the amount does not equal the cart total, the order is flagged.
2.  **Marketing Insights:**
    The `summary` function was refactored. We loop over all enriched orders and tap into `order.meta.channel` and `order.meta.coupon`. The payload now natively outputs GMV splits by channel (e.g., App vs Web) and coupon usages (e.g., `FESTIVE15`).
3.  **Returns & Refunds:**
    The exact overall `return_rate` and `refund_rate` are returned in `/analytics/summary`.
4.  **Funnel Fixes:**
    The funnel metric separates *Paid* statuses cleanly, handling pending CODs dynamically as instructed.

## 5. Testing & Verification

A core tenet of our implementation was the `"Run It" Rule`. 

Under the `tests/` directory, two new files were synthesized:
*   **`test_models.py`:** Proved that Pydantic properly swallows impossible dates, sets `null` items to `[]`, and avoids crashing on corrupted customer structures.
*   **`test_analytics.py`:** Tested computational robustness mathematically, ensuring that `enrich_order` accurately identifies the `PAYMENT_AMOUNT_MISMATCH` flag, and validated the marketing efficacy tracking logic dynamically.

We used `pytest` to execute all assertions, which now pass successfully at 100%.

The implementation was sealed behind atomic Git commits (`feat(models): implement defensive pydantic...` and `feat(analytics): add GMV mismatch validation...`). The API is now scalable, resilient, and business-focused!
