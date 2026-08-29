package main

import (
	"math"
	"testing"
)

func TestLineTotalCentsRoundsHalfUp(t *testing.T) {
	cases := []struct {
		qty       int
		unitPrice float64
		wantCents int64
	}{
		{3, 19.99, 5997},
		{1, 0.125, 13},
		{2, 0.125, 25},
		{2, 10.05, 2010},
		{1, 0.1, 10},
	}
	for _, c := range cases {
		if got := lineTotalCents(c.qty, c.unitPrice); got != c.wantCents {
			t.Errorf("lineTotalCents(%d, %v) = %d, want %d", c.qty, c.unitPrice, got, c.wantCents)
		}
	}
}

func TestOrderTotalSumsRoundedLines(t *testing.T) {
	items := []Line{{Quantity: 3, UnitPrice: 19.99}, {Quantity: 2, UnitPrice: 5.0}}
	if got := orderTotal(items); math.Abs(got-69.97) > 1e-9 {
		t.Errorf("orderTotal = %v, want 69.97", got)
	}
}

func TestOrderTotalEmptyIsZero(t *testing.T) {
	if got := orderTotal(nil); got != 0 {
		t.Errorf("orderTotal(nil) = %v, want 0", got)
	}
}
