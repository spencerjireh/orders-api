<?php

declare(strict_types=1);

namespace Orders;

/**
 * Money math for orders: every line rounds to the cent, half up, before the
 * lines are summed, which is how the line items on a printed invoice add up.
 */
final class Pricing
{
    /** One line's total in integer cents, rounded half up. */
    public static function lineTotalCents(int $quantity, float $unitPrice): int
    {
        return (int) round($quantity * $unitPrice * 100, 0, PHP_ROUND_HALF_UP);
    }

    /**
     * @param array<int, array{quantity: int, unit_price: float}> $items
     */
    public static function orderTotal(array $items): float
    {
        $cents = 0;
        foreach ($items as $item) {
            $cents += self::lineTotalCents($item['quantity'], $item['unit_price']);
        }
        return $cents / 100;
    }
}
