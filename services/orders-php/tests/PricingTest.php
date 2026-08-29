<?php

declare(strict_types=1);

namespace Orders\Tests;

use Orders\Pricing;
use PHPUnit\Framework\Attributes\DataProvider;
use PHPUnit\Framework\Attributes\Test;
use PHPUnit\Framework\TestCase;

final class PricingTest extends TestCase
{
    public static function lines(): array
    {
        return [
            [3, 19.99, 5997],
            [1, 0.125, 13],
            [2, 0.125, 25],
            [2, 10.05, 2010],
            [1, 0.1, 10],
        ];
    }

    #[DataProvider('lines')]
    #[Test]
    public function rounds_each_line_half_up(int $quantity, float $unitPrice, int $wantCents): void
    {
        self::assertSame($wantCents, Pricing::lineTotalCents($quantity, $unitPrice));
    }

    #[Test]
    public function sums_the_rounded_lines(): void
    {
        $items = [
            ['quantity' => 3, 'unit_price' => 19.99],
            ['quantity' => 2, 'unit_price' => 5.0],
        ];
        self::assertSame(69.97, Pricing::orderTotal($items));
    }

    #[Test]
    public function empty_order_totals_zero(): void
    {
        self::assertSame(0.0, Pricing::orderTotal([]));
    }
}
