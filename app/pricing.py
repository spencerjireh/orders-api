"""Money math for orders.

Prices are floats at the API edge; every calculation here goes through
Decimal so half-cent values round predictably, not the way binary floats do.
Each line is rounded to the cent before the lines are summed, which is how the
line items on a printed invoice add up.

Half-cent values use banker's rounding (half to even), which is the usual
default in financial software because it does not bias a long run of sums
upward the way half-up does.
"""

from decimal import ROUND_HALF_EVEN, Decimal
from typing import Protocol

CENT = Decimal("0.01")


class Line(Protocol):
    quantity: int
    unit_price: float


def line_total(quantity: int, unit_price: float) -> Decimal:
    """One line, rounded to the cent."""
    amount = Decimal(str(unit_price)) * quantity
    return amount.quantize(CENT, rounding=ROUND_HALF_EVEN)


def order_total(items: list[Line]) -> float:
    """Sum of the rounded line totals, as the float the API returns."""
    total = sum((line_total(item.quantity, item.unit_price) for item in items), Decimal("0"))
    return float(total.quantize(CENT, rounding=ROUND_HALF_EVEN))
