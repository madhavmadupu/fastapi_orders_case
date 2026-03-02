from __future__ import annotations
from typing import List, Optional, Literal, Any
from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.utils import parse_dt

def validate_date_string(v: Any) -> str | None:
    if not isinstance(v, str):
        return None
    dt = parse_dt(v)
    if dt is None:
        return None
    return dt.isoformat()

class Customer(BaseModel):
    model_config = ConfigDict(extra="ignore")
    customer_id: str = "unknown"
    name: str = "Unknown"
    tier: Optional[Literal["premium","standard","trial"]] = None
    city: Optional[str] = None
    phone: Optional[str] = None

class Item(BaseModel):
    model_config = ConfigDict(extra="ignore")
    sku: str
    name: str
    qty: int = Field(default=1, ge=1)
    unit_price: int = Field(default=0, ge=0)

class Pricing(BaseModel):
    model_config = ConfigDict(extra="ignore")
    discount: int = 0
    tax: int = 0
    currency: str = "INR"

class Payment(BaseModel):
    model_config = ConfigDict(extra="ignore")
    method: str = "unknown"
    status: str = "unknown"
    amount: int = 0
    time: str | None = None

    @field_validator("time", mode="before")
    @classmethod
    def validate_time(cls, v: Any) -> str | None:
        return validate_date_string(v)

class Shipment(BaseModel):
    model_config = ConfigDict(extra="ignore")
    carrier: str = "unknown"
    status: str = "unknown"
    shipped_at: Optional[str] = None
    delivered_at: Optional[str] = None
    returned_at: Optional[str] = None

    @field_validator("shipped_at", "delivered_at", "returned_at", mode="before")
    @classmethod
    def validate_times(cls, v: Any) -> str | None:
        return validate_date_string(v)

class Event(BaseModel):
    model_config = ConfigDict(extra="ignore")
    time: str | None = None
    type: str = "unknown"

    @field_validator("time", mode="before")
    @classmethod
    def validate_time(cls, v: Any) -> str | None:
        return validate_date_string(v)

class Order(BaseModel):
    model_config = ConfigDict(extra="ignore")
    order_id: str
    created_at: str | None = None
    customer: Customer
    items: List[Item] = Field(default_factory=list)
    pricing: Pricing = Field(default_factory=Pricing)
    payments: List[Payment] = Field(default_factory=list)
    shipments: List[Shipment] = Field(default_factory=list)
    events: List[Event] = Field(default_factory=list)
    meta: Optional[dict[str, Any]] = None

    @field_validator("created_at", mode="before")
    @classmethod
    def validate_created_at(cls, v: Any) -> str | None:
        return validate_date_string(v)

    @field_validator("items", mode="before")
    @classmethod
    def cast_null_items(cls, v: Any) -> List[Any]:
        if v is None:
            return []
        if not isinstance(v, list):
            return []
        return v

    @field_validator("customer", mode="before")
    @classmethod
    def cast_invalid_customer(cls, v: Any) -> Any:
        # If customer isn't a dict, fallback to a dummy dict
        if not isinstance(v, dict):
            return {"customer_id": "unknown", "name": "Unknown"}
        return v

class EnrichedOrder(BaseModel):
    model_config = ConfigDict(extra="ignore")
    order_id: str
    created_at: str | None = None
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
    risk_flags: List[str] = Field(default_factory=list)
