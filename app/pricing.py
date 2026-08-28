"""Money math for orders.

Prices are floats at the API edge; every calculation here goes through
Decimal so half-cent values round the way an invoice does (half up), not the
way binary floats do. Each line is rounded to the cent before the lines are
summed, which is how the line items on a printed invoice add up.

Half up rather than banker's rounding, deliberately. Half to even is the
better default for a long run of sums, because it does not bias the total
upward — but it makes a single line disagree with the printed receipt: a
1.005 line shows as 1.00 next to a 2.005 line that shows as 2.00, and the
customer's total is a cent under what they were quoted. The suite pins this;
see test_order_total_rounding.
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
    """Sum of the rounded line totals, as the float the API returns."""
    total = sum((line_total(item.quantity, item.unit_price) for item in items), Decimal("0"))
    return float(total.quantize(CENT, rounding=ROUND_HALF_UP))
