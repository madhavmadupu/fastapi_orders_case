from __future__ import annotations
from typing import List, Optional, Literal, Any
from pydantic import BaseModel, Field

class Customer(BaseModel):
    customer_id: str
    name: str
    tier: Optional[Literal["premium","standard","trial"]] = None
    city: Optional[str] = None
    phone: Optional[str] = None

class Item(BaseModel):
    sku: str
    name: str
    qty: int = Field(ge=1)
    unit_price: int = Field(ge=0)

class Pricing(BaseModel):
    discount: int = 0
    tax: int = 0
    currency: str = "INR"

class Payment(BaseModel):
    method: str
    status: str
    amount: int = 0
    time: str

class Shipment(BaseModel):
    carrier: str
    status: str
    shipped_at: Optional[str] = None
    delivered_at: Optional[str] = None
    returned_at: Optional[str] = None

class Event(BaseModel):
    time: str
    type: str

class Order(BaseModel):
    order_id: str
    created_at: str
    customer: Customer
    items: List[Item]
    pricing: Pricing = Pricing()
    payments: List[Payment] = []
    shipments: List[Shipment] = []
    events: List[Event] = []
    meta: Optional[dict[str, Any]] = None

class EnrichedOrder(BaseModel):
    order_id: str
    created_at: str
    customer: Customer
    items: List[Item]
    order_value: int
    discount_total: int
    tax_total: int
    net_payable: int
    paid_amount: int
    payment_status: str
    fulfillment_status: str
    delivery_tat_hours: Optional[float] = None
    risk_flags: List[str] = []
