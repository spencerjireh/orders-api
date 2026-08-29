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


def to_cent(amount: Decimal) -> Decimal:
    """Round to the cent, half up.

    The rounding mode is the whole point of this module, and it was written
    out at each call site. One helper means a future caller cannot quietly
    pick a different mode -- and `ROUND_HALF_UP` appears once, where it can be
    read against the docstring above rather than checked twice.
    """
    return amount.quantize(CENT, rounding=ROUND_HALF_UP)


def line_total(quantity: int, unit_price: float) -> Decimal:
    """One line, rounded to the cent."""
    amount = Decimal(str(unit_price)) * quantity
    return to_cent(amount)


def order_total(items: list[Line]) -> float:
    """Sum of the rounded line totals, as the float the API returns."""
    total = sum((line_total(item.quantity, item.unit_price) for item in items), Decimal("0"))
    return float(to_cent(total))
