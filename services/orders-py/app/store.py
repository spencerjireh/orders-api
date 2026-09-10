"""Simple in-memory order storage."""

from datetime import UTC, datetime
from itertools import count, islice

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
    """One page of orders, filtered before it is paginated.

    The filter stays ahead of the pagination, so a page is the same page it
    always was; only the materialising changed. Iterating lazily and cutting
    the page with islice means a request for the first page stops after it
    has seen offset + limit matches, instead of building a list of every
    order and then throwing most of it away.

    islice requires non-negative bounds, which is what the route already
    enforces (limit gt=0 le=100, offset ge=0).
    """
    orders = iter(_orders.values())
    if status is not None:
        orders = (order for order in orders if order.status == status)
    return list(islice(orders, offset, offset + limit))


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
