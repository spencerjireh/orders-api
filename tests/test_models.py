"""The validation boundary: what the API refuses before pricing ever runs.

`app/pricing.py` is deliberately total — `line_total(0, ...)` returns `0.00`
and `order_total([])` returns `0.0` rather than raising. That is safe, but it
means the pricing helpers are not where a nonsensical order is caught. The
models are, and nothing pinned that.
"""

import pytest
from pydantic import ValidationError

from app.models import OrderCreate, OrderItem


def test_a_line_must_have_a_positive_quantity() -> None:
    """`quantity` is `gt=0`, so a zero-quantity line never reaches pricing."""
    with pytest.raises(ValidationError):
        OrderItem(product_id="sku", quantity=0, unit_price=9.99)


def test_a_line_must_have_a_positive_price() -> None:
    """`unit_price` is `gt=0`: a free line is a data error, not a discount."""
    with pytest.raises(ValidationError):
        OrderItem(product_id="sku", quantity=1, unit_price=0)


def test_a_line_must_name_a_product() -> None:
    with pytest.raises(ValidationError):
        OrderItem(product_id="", quantity=1, unit_price=9.99)


def test_an_order_must_have_at_least_one_line() -> None:
    """`items` is `min_length=1`, so an empty order is rejected at the edge."""
    with pytest.raises(ValidationError):
        OrderCreate(customer_email="buyer@example.com", items=[])


def test_a_well_formed_order_is_accepted() -> None:
    """The negative cases above are meaningless without this one passing."""
    order = OrderCreate(
        customer_email="buyer@example.com",
        items=[OrderItem(product_id="sku", quantity=2, unit_price=9.99)],
    )
    assert order.items[0].quantity == 2
