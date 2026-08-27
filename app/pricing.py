"""Money math for orders.

Prices are floats at the API edge; every calculation here goes through
Decimal so half-cent values round the way an invoice does (half up), not the
way binary floats do. The order is rounded once, at the end, so the total does
not accumulate a rounding step per line.
"""

from decimal import ROUND_HALF_UP, Decimal
from typing import Protocol

CENT = Decimal("0.01")


class Line(Protocol):
    quantity: int
    unit_price: float


def line_total(quantity: int, unit_price: float) -> Decimal:
    """One line, rounded to the cent."""
    amount = Decimal(str(unit_price)) * quantity
    return amount.quantize(CENT, rounding=ROUND_HALF_UP)


def order_total(items: list[Line]) -> float:
    """Sum of the lines, rounded once at the end, as the float the API returns."""
    total = sum((Decimal(str(item.unit_price)) * item.quantity for item in items), Decimal("0"))
    return float(total.quantize(CENT, rounding=ROUND_HALF_UP))
