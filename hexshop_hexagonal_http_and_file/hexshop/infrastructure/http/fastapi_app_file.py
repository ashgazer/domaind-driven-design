from __future__ import annotations
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid, os
from ...domain.entities import Customer
from ...domain.services.discounts import DiscountService
from ..persistence.file_order_repository import FileOrderRepository
from ...application.use_cases import CheckoutService

app = FastAPI(title="HexShop API (file-backed)")

repo_path = os.environ.get("REPO_FILE", "./orders.json")
repo = FileOrderRepository(repo_path)
discounts = DiscountService()
checkout = CheckoutService(repo, discounts)

# naive in-memory customers (you can swap for a file-backed port similarly)
CUSTOMERS: dict[str, Customer] = {}

class CustomerCreate(BaseModel):
    name: str
    email: str

class OrderStart(BaseModel):
    customer_id: str
    product_id: str
    unit_price_pence: int
    quantity: int

class AddItem(BaseModel):
    product_id: str
    unit_price_pence: int
    quantity: int

@app.post("/customers")
def create_customer(payload: CustomerCreate):
    c = Customer.new(payload.name, payload.email)
    CUSTOMERS[str(c.id)] = c
    return {"customer_id": str(c.id)}

@app.post("/orders")
def start_order(payload: OrderStart):
    cid = payload.customer_id
    if cid not in CUSTOMERS:
        raise HTTPException(404, "customer not found")
    order_id = checkout.start_order_with_item(
        CUSTOMERS[cid], payload.product_id, payload.unit_price_pence, payload.quantity
    )
    return {"order_id": str(order_id)}

@app.post("/orders/{order_id}/items")
def add_item(order_id: str, payload: AddItem):
    try:
        checkout.add_item(uuid.UUID(order_id), payload.product_id, payload.unit_price_pence, payload.quantity)
        return {"ok": True}
    except ValueError as e:
        raise HTTPException(400, str(e))

@app.get("/orders/{order_id}/preview")
def preview(order_id: str, threshold_pence: int = 2000, discount_pct: int = 10):
    try:
        total = checkout.preview_total_with_discount(uuid.UUID(order_id), threshold_pence, discount_pct)
        return {"discounted_total_pence": total.amount, "currency": total.currency}
    except ValueError as e:
        raise HTTPException(404, str(e))

@app.post("/orders/{order_id}/submit")
def submit(order_id: str):
    try:
        total = checkout.submit(uuid.UUID(order_id))
        return {"total_pence": total.amount, "currency": total.currency}
    except ValueError as e:
        raise HTTPException(400, str(e))

@app.get("/orders/{order_id}")
def get_order(order_id: str):
    o = repo.get(uuid.UUID(order_id))
    if not o:
        raise HTTPException(404, "order not found")
    return {
        "id": str(o.id),
        "customer_id": str(o.customer_id),
        "is_submitted": o.is_submitted(),
        "items": [
            {"product_id": it.product_id.value, "unit_price_pence": it.unit_price.amount, "qty": it.quantity}
            for it in o.items()
        ],
        "total_pence": o.total().amount,
    }
