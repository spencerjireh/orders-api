//! Demo Rust orders service. Money math: every line rounds to the cent,
//! half away from zero (half up for the positive prices an order carries),
//! before the lines are summed.

use serde::{Deserialize, Serialize};

/// One item on an order.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Line {
    pub quantity: i64,
    pub unit_price: f64,
}

/// One line's total in integer cents, rounded half up.
pub fn line_total_cents(quantity: i64, unit_price: f64) -> i64 {
    (quantity as f64 * unit_price * 100.0).round() as i64
}

/// Sum of the rounded line totals, in dollars.
pub fn order_total(items: &[Line]) -> f64 {
    let cents: i64 = items
        .iter()
        .map(|item| line_total_cents(item.quantity, item.unit_price))
        .sum();
    cents as f64 / 100.0
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn rounds_each_line_half_up() {
        assert_eq!(line_total_cents(3, 19.99), 5997);
        assert_eq!(line_total_cents(1, 0.125), 13);
        assert_eq!(line_total_cents(2, 0.125), 25);
        assert_eq!(line_total_cents(2, 10.05), 2010);
        assert_eq!(line_total_cents(1, 0.1), 10);
    }

    #[test]
    fn sums_rounded_lines() {
        let items = vec![
            Line { quantity: 3, unit_price: 19.99 },
            Line { quantity: 2, unit_price: 5.0 },
        ];
        assert!((order_total(&items) - 69.97).abs() < 1e-9);
    }

    #[test]
    fn empty_order_totals_zero() {
        assert_eq!(order_total(&[]), 0.0);
    }
}
