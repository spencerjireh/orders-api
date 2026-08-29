"""`line_totals` must add up to `order_total`, not merely near it."""

from dataclasses import dataclass

from app.pricing import line_totals, order_total


@dataclass
class Item:
    quantity: int
    unit_price: float


def test_the_printed_lines_sum_to_the_printed_total() -> None:
    items = [Item(3, 0.125), Item(2, 1.005), Item(1, 19.99)]
    assert round(sum(line_totals(items)), 2) == order_total(items)


def test_an_empty_order_has_no_lines_and_no_total() -> None:
    assert line_totals([]) == []
    assert order_total([]) == 0.0


def test_each_line_is_rounded_half_up() -> None:
    assert line_totals([Item(1, 0.125), Item(1, 0.135)]) == [0.13, 0.14]
