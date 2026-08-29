"""Per-line totals, and the total they must add up to."""

from dataclasses import dataclass


@dataclass
class _Line:
    quantity: int
    unit_price: float
