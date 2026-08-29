import { describe, expect, it } from "vitest";
import { lineTotalCents, orderTotal } from "../src/pricing.mjs";

describe("lineTotalCents", () => {
  it("rounds each line half up to the cent", () => {
    expect(lineTotalCents(3, 19.99)).toBe(5997);
    expect(lineTotalCents(1, 0.125)).toBe(13);
    expect(lineTotalCents(2, 0.125)).toBe(25);
  });

  it("keeps whole cents exact", () => {
    expect(lineTotalCents(2, 10.05)).toBe(2010);
    expect(lineTotalCents(1, 0.1)).toBe(10);
  });
});

describe("orderTotal", () => {
  it("sums the rounded line totals", () => {
    const items = [
      { quantity: 3, unitPrice: 19.99 },
      { quantity: 2, unitPrice: 5.0 },
    ];
    expect(orderTotal(items)).toBeCloseTo(69.97, 10);
  });

  it("totals zero for an empty order", () => {
    expect(orderTotal([])).toBe(0);
  });
});
