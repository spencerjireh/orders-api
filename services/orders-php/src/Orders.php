<?php

declare(strict_types=1);

namespace Orders;

/**
 * In-memory order store and the routing behind public/index.php. Routing is a
 * plain function so the tests can drive it without a server.
 */
final class Orders
{
    /** @var array<int, array<string, mixed>> */
    private array $orders = [];
    private int $nextId = 1;

    /**
     * @return array{status: int, body: array<string, mixed>|array<int, mixed>|string}
     */
    public function handle(string $method, string $path, ?string $body): array
    {
        $path = strtok($path, '?') ?: $path;

        if ($method === 'GET' && $path === '/health') {
            return ['status' => 200, 'body' => ['status' => 'ok']];
        }
        if ($method === 'POST' && $path === '/orders') {
            $payload = json_decode($body ?? '', true);
            $customer = is_array($payload) ? ($payload['customer'] ?? '') : '';
            $items = is_array($payload) ? ($payload['items'] ?? []) : [];
            if (!is_string($customer) || $customer === '' || !is_array($items) || $items === []) {
                return ['status' => 400, 'body' => ['detail' => 'customer and a non-empty items list are required']];
            }
            $order = [
                'id' => $this->nextId++,
                'customer' => $customer,
                'items' => $items,
                'status' => 'open',
                'total' => Pricing::orderTotal($items),
            ];
            $this->orders[$order['id']] = $order;
            return ['status' => 201, 'body' => $order];
        }
        if ($method === 'GET' && $path === '/orders') {
            return ['status' => 200, 'body' => array_values($this->orders)];
        }
        if ($method === 'GET' && str_starts_with($path, '/orders/')) {
            $id = substr($path, strlen('/orders/'));
            if (!ctype_digit($id)) {
                return ['status' => 400, 'body' => ['detail' => 'order id must be an integer']];
            }
            if (isset($this->orders[(int) $id])) {
                return ['status' => 200, 'body' => $this->orders[(int) $id]];
            }
            return ['status' => 404, 'body' => ['detail' => "Order $id not found"]];
        }
        return ['status' => 404, 'body' => ['detail' => 'not found']];
    }
}
