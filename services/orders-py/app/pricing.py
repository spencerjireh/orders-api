"""Money math for orders.

Prices are floats at the API edge; every calculation here goes through
Decimal so half-cent values round the way an invoice does (half up), not the
way binary floats do. Each line is rounded to the cent before the lines are
summed, which is how the line items on a printed invoice add up.
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
    """Sum of the rounded line totals, as the float the API returns.

    No second quantize: every term is already exact at the cent, and adding
    Decimals at the cent cannot produce a third decimal place. Rounding again
    could only ever be a no-op, so it read as if the sum were lossy.
    """
    total = sum((line_total(item.quantity, item.unit_price) for item in items), Decimal("0"))
    return float(total)
