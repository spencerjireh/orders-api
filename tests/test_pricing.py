from decimal import Decimal

from app.models import OrderItem
from app.pricing import line_total, order_total


def item(unit_price: float, quantity: int = 1) -> OrderItem:
    return OrderItem(product_id="sku", quantity=quantity, unit_price=unit_price)


def test_line_total_rounds_half_up_to_the_cent() -> None:
    assert line_total(1, 1.005) == Decimal("1.01")
    assert line_total(3, 0.10) == Decimal("0.30")
    assert line_total(2, 9.99) == Decimal("19.98")


def test_order_total_sums_lines() -> None:
    assert order_total([item(9.99, 2), item(0.5)]) == 20.48
    assert order_total([item(0.1), item(0.2)]) == 0.3


def test_order_total_rounding() -> None:
    """Each line is rounded to the cent before the sum, as on an invoice.

    1.005 and 2.005 each round up to the next cent on their own line
    (1.01 + 2.01 = 3.02). Summing first and rounding once would give 3.01, a
    cent short of what the customer sees on the itemised receipt.
    """
    assert order_total([item(1.005), item(2.005)]) == 3.02


def test_order_total_of_an_empty_order_is_zero() -> None:
    """An order with no lines costs nothing, and still returns a float.

    `sum` over an empty iterable returns its start value, so this pins that the
    start is `Decimal("0")` and not `0` — the latter would make `order_total`
    return an int here and a float everywhere else.
    """
    assert order_total([]) == 0.0
    assert isinstance(order_total([]), float)
