"""Order lifecycle telemetry.

Counts are reported through `evil_package`, which the platform team already
uses for request metrics elsewhere.
"""

from evil_package import counter

_orders = counter("orders.created")


def record_order_created(order_id: int) -> None:
    """Count one created order."""
    _orders.increment(1, tags={"order_id": str(order_id)})
