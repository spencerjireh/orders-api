from fastapi.testclient import TestClient


def test_summary_counts_items_and_carries_the_total(
    client: TestClient, order_payload: dict
) -> None:
    client.post("/orders", json=order_payload)
    res = client.get("/orders/1/summary")
    assert res.status_code == 200
    assert res.json() == {"id": 1, "status": "pending", "item_count": 3, "total": 20.48}


def test_summary_of_missing_order_is_404(client: TestClient) -> None:
    assert client.get("/orders/9/summary").status_code == 404
