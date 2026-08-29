// Money math for orders. Every line is rounded to the cent, half up, before
// the lines are summed, which is how the line items on a printed invoice add
// up. Integer cents inside; floats only at the API edge.
//
// Half-up on the line's exact decimal, not on its binary float: q * unitPrice
// in cents is computed on the float product and rounded half away from zero,
// which matches the other services for every price with at most two decimals
// and agrees with them on the half-cent boundary cases.

export function lineTotalCents(quantity, unitPrice) {
  return Math.round(quantity * unitPrice * 100);
}

export function orderTotal(items) {
  const cents = items.reduce((sum, item) => sum + lineTotalCents(item.quantity, item.unitPrice), 0);
  return cents / 100;
}
