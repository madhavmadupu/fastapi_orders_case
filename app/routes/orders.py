from __future__ import annotations
from fastapi import APIRouter, HTTPException, Query, Depends, status
from typing import Optional
from app.models import Order
from app.repositories.order_repository import OrderRepository, get_order_repository

router = APIRouter(tags=["orders"])

@router.get("/orders/{order_id}")
def get_order(
    order_id: str,
    repository: OrderRepository = Depends(get_order_repository)
):
    o = repository.get_by_id(order_id)
    if not o:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="order not found")
    return o

@router.get("/orders")
def search_orders(
    status: Optional[str] = Query(default=None, description="fulfillment status: pending/shipped/delivered/returned"),
    payment_status: Optional[str] = Query(default=None, description="paid/partial/unpaid/refunded/cod_pending"),
    city: Optional[str] = None,
    customer_tier: Optional[str] = None,
    min_value: Optional[int] = Query(default=None, ge=0),
    max_value: Optional[int] = Query(default=None, ge=0),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
    repository: OrderRepository = Depends(get_order_repository)
):
    return repository.search(status, payment_status, city, customer_tier, min_value, max_value, page, page_size)

@router.post("/orders", status_code=status.HTTP_201_CREATED)
def create_order(
    order: Order,
    repository: OrderRepository = Depends(get_order_repository)
):
    existing = repository.get_by_id(order.order_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Order with id {order.order_id} already exists."
        )
    return repository.create(order)

@router.put("/orders/{order_id}")
def update_order(
    order_id: str,
    order: Order,
    repository: OrderRepository = Depends(get_order_repository)
):
    if order.order_id != order_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order ID in payload does not match URL path."
        )
    
    updated = repository.update(order_id, order)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="order not found")
    
    return updated

@router.delete("/orders/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order(
    order_id: str,
    repository: OrderRepository = Depends(get_order_repository)
):
    deleted = repository.delete(order_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="order not found")
    return None
