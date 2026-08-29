from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app import store
from app.main import app


@pytest.fixture
def client() -> Iterator[TestClient]:
    store.reset()
    with TestClient(app) as c:
        yield c
    store.reset()


@pytest.fixture
def order_payload() -> dict:
    return {
        "customer_email": "ada@example.com",
        "items": [
            {"product_id": "sku-1", "quantity": 2, "unit_price": 9.99},
            {"product_id": "sku-2", "quantity": 1, "unit_price": 0.5},
        ],
    }
