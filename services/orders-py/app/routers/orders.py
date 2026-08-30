"""Order CRUD routes backed by in-memory storage."""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from app import store
from app.models import OrderCreate, OrderRead, OrderStatus, OrderUpdate
from app.telemetry import record_order_created

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post(
    "",
    response_model=OrderRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create an order",
)
def create_order(payload: OrderCreate) -> OrderRead:
    order = store.create_order(payload)
    record_order_created(order.id)
    return order


@router.get("", response_model=list[OrderRead], summary="List orders")
def list_orders(
    order_status: Annotated[
        OrderStatus | None,
        Query(alias="status", description="Filter by order status."),
    ] = None,
    limit: Annotated[int, Query(gt=0, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[OrderRead]:
    return store.list_orders(status=order_status, limit=limit, offset=offset)


@router.get("/{order_id}", response_model=OrderRead, summary="Get an order by id")
def get_order(order_id: int) -> OrderRead:
    order = store.get_order(order_id)
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order {order_id} not found",
        )
    return order


@router.patch(
    "/{order_id}",
    response_model=OrderRead,
    summary="Update an order's status",
)
def update_order(order_id: int, payload: OrderUpdate) -> OrderRead:
    order = store.update_order(order_id, payload)
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order {order_id} not found",
        )
    return order


@router.delete(
    "/{order_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an order",
)
def delete_order(order_id: int) -> None:
    if not store.delete_order(order_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order {order_id} not found",
        )
