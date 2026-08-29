from fastapi.testclient import TestClient


def test_create_and_get_order(client: TestClient, order_payload: dict) -> None:
    created = client.post("/orders", json=order_payload)
    assert created.status_code == 201
    body = created.json()
    assert body["id"] == 1
    assert body["status"] == "pending"
    assert body["total"] == 20.48

    fetched = client.get("/orders/1")
    assert fetched.status_code == 200
    assert fetched.json() == body


def test_list_orders_filters_by_status_and_pages(client: TestClient, order_payload: dict) -> None:
    for _ in range(3):
        assert client.post("/orders", json=order_payload).status_code == 201
    assert client.patch("/orders/2", json={"status": "paid"}).status_code == 200

    everything = client.get("/orders").json()
    assert [o["id"] for o in everything] == [1, 2, 3]
    paid = client.get("/orders", params={"status": "paid"}).json()
    assert [o["id"] for o in paid] == [2]
    page = client.get("/orders", params={"limit": 1, "offset": 1}).json()
    assert [o["id"] for o in page] == [2]


def test_update_and_delete_order(client: TestClient, order_payload: dict) -> None:
    client.post("/orders", json=order_payload)
    updated = client.patch("/orders/1", json={"status": "shipped"})
    assert updated.status_code == 200
    assert updated.json()["status"] == "shipped"

    assert client.delete("/orders/1").status_code == 204
    assert client.get("/orders/1").status_code == 404
    assert client.delete("/orders/1").status_code == 404
    assert client.patch("/orders/1", json={"status": "paid"}).status_code == 404


def test_rejects_bad_payloads(client: TestClient, order_payload: dict) -> None:
    no_items = {**order_payload, "items": []}
    assert client.post("/orders", json=no_items).status_code == 422
    bad_email = {**order_payload, "customer_email": "not-an-email"}
    assert client.post("/orders", json=bad_email).status_code == 422
    free = {**order_payload, "items": [{"product_id": "x", "quantity": 1, "unit_price": 0}]}
    assert client.post("/orders", json=free).status_code == 422
