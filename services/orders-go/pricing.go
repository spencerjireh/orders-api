// Package main is the Go orders service. Money math lives here: every line
// rounds to the cent, half away from zero (half up for the positive prices an
// order carries), before the lines are summed.
package main

import "math"

// Line is one item on an order.
type Line struct {
	Quantity  int     `json:"quantity"`
	UnitPrice float64 `json:"unit_price"`
}

// lineTotalCents returns one line's total in integer cents, rounded half up.
func lineTotalCents(quantity int, unitPrice float64) int64 {
	return int64(math.Round(float64(quantity) * unitPrice * 100))
}

// orderTotal sums the rounded line totals and returns dollars as a float.
func orderTotal(items []Line) float64 {
	var cents int64
	for _, item := range items {
		cents += lineTotalCents(item.Quantity, item.UnitPrice)
	}
	return float64(cents) / 100
}
