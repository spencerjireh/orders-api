<?php

declare(strict_types=1);

namespace Orders\Tests;

use Orders\Orders;
use PHPUnit\Framework\Attributes\Test;
use PHPUnit\Framework\TestCase;

final class OrdersTest extends TestCase
{
    #[Test]
    public function health_is_ok(): void
    {
        $response = (new Orders())->handle('GET', '/health', null);
        self::assertSame(200, $response['status']);
        self::assertSame(['status' => 'ok'], $response['body']);
    }

    #[Test]
    public function create_then_read_back(): void
    {
        $orders = new Orders();
        $created = $orders->handle(
            'POST',
            '/orders',
            '{"customer":"ada","items":[{"quantity":3,"unit_price":19.99}]}'
        );
        self::assertSame(201, $created['status']);
        self::assertSame(59.97, $created['body']['total']);

        $fetched = $orders->handle('GET', '/orders/1', null);
        self::assertSame(200, $fetched['status']);
        self::assertSame('ada', $fetched['body']['customer']);
    }

    #[Test]
    public function empty_items_is_rejected(): void
    {
        $response = (new Orders())->handle('POST', '/orders', '{"customer":"ada","items":[]}');
        self::assertSame(400, $response['status']);
    }

    #[Test]
    public function unknown_order_is_404(): void
    {
        $response = (new Orders())->handle('GET', '/orders/9999', null);
        self::assertSame(404, $response['status']);
    }

    #[Test]
    public function non_integer_id_is_400(): void
    {
        $response = (new Orders())->handle('GET', '/orders/abc', null);
        self::assertSame(400, $response['status']);
    }
}
