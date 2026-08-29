"""Simple in-memory order storage."""

from datetime import UTC, datetime
from itertools import count

from app.models import OrderCreate, OrderRead, OrderStatus, OrderUpdate

_orders: dict[int, OrderRead] = {}
_ids = count(start=1)


def create_order(payload: OrderCreate) -> OrderRead:
    order_id = next(_ids)
    order = OrderRead(
        id=order_id,
        status=OrderStatus.PENDING,
        created_at=datetime.now(UTC),
        **payload.model_dump(),
    )
    _orders[order_id] = order
    return order


def get_order(order_id: int) -> OrderRead | None:
    return _orders.get(order_id)


def list_orders(
    status: OrderStatus | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[OrderRead]:
    orders = list(_orders.values())
    if status is not None:
        orders = [order for order in orders if order.status == status]
    return orders[offset : offset + limit]


def update_order(order_id: int, payload: OrderUpdate) -> OrderRead | None:
    order = _orders.get(order_id)
    if order is None:
        return None
    updated = order.model_copy(update={"status": payload.status})
    _orders[order_id] = updated
    return updated


def delete_order(order_id: int) -> bool:
    return _orders.pop(order_id, None) is not None


def reset() -> None:
    """Forget every order and start ids from 1 again (tests)."""
    global _ids
    _orders.clear()
    _ids = count(start=1)
