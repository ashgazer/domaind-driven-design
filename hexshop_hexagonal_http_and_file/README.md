# HexShop — Hexagonal (Ports & Adapters)

This version adds two new adapters:
1) **HTTP adapter** using FastAPI (run with `make server`).
2) **File-backed repository** adapter (JSON on disk) + HTTP server using it (`make server-file`).

## Install
```bash
python -m pip install -U pytest fastapi uvicorn
```

## Run
```bash
make test
make demo
make server        # in-memory repo
make server-file   # file-backed repo (env: REPO_FILE=./orders.json)
```

### HTTP Endpoints (both servers expose the same API)
- `POST /customers` → Create a customer (returns `customer_id`)
- `POST /orders` → Start order with first item
  - body: `{ "customer_id": "...uuid...", "product_id": "SKU", "unit_price_pence": 250, "quantity": 2 }`
- `POST /orders/{order_id}/items` → Add item
- `GET /orders/{order_id}/preview?threshold_pence=2000&discount_pct=10` → Discounted preview
- `POST /orders/{order_id}/submit` → Submit and return total
- `GET /orders/{order_id}` → Inspect order

All state is in-memory for `make server`, or persisted to `orders.json` for `make server-file`.
