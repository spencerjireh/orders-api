<?php

declare(strict_types=1);

/**
 * Router for `php -S 127.0.0.1:8006 public/index.php`. The store lives for
 * the life of the server process, which is what a smoke check exercises.
 */

require __DIR__ . '/../vendor/autoload.php';

use Orders\Orders;

$orders = new Orders();
$method = $_SERVER['REQUEST_METHOD'];
$path = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH) ?: '/';
$body = file_get_contents('php://input') ?: null;

$response = $orders->handle($method, $path, $body);

http_response_code($response['status']);
header('Content-Type: application/json');
echo json_encode($response['body'], JSON_UNESCAPED_SLASHES);
