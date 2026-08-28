# Orders API

A small FastAPI service that manages orders with simple in-memory storage. It
is a demo "victim" application that a security tool protects.

## Requirements

- Python 3.12+

## Run

Install dependencies (a virtualenv is recommended):

```bash
pip install -r requirements.txt
```

Run the tests:

```bash
pip install -e '.[dev]'
python -m pytest -q
```

Start the development server:

```bash
uvicorn app.main:app --reload
```

The service listens on `http://127.0.0.1:8000`. Interactive docs are available
at `/docs` (Swagger UI) and `/redoc`.

## Endpoints

| Method   | Path           | Description              |
| -------- | -------------- | ------------------------ |
| `GET`    | `/health`      | Service health check     |
| `POST`   | `/orders`      | Create an order          |
| `GET`    | `/orders`      | List orders (paginated)  |
| `GET`    | `/orders/{id}` | Get an order by id       |
| `PATCH`  | `/orders/{id}` | Update an order's status |
| `DELETE` | `/orders/{id}` | Delete an order          |

### Example

```bash
curl -X POST http://127.0.0.1:8000/orders \
  -H "Content-Type: application/json" \
  -d '{
    "customer_email": "ada@example.com",
    "items": [
      {"product_id": "SKU-001", "quantity": 2, "unit_price": 9.99}
    ]
  }'
```

```bash
curl http://127.0.0.1:8000/orders/1
```

## Notes

- Storage is in-memory. All orders are lost when the process restarts.
- This service intentionally has no authentication. It exists to be protected
  by an external security tool.
