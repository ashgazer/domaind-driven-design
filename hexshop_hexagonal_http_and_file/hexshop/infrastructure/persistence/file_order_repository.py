from __future__ import annotations
from typing import Dict, List, Optional
import uuid, json, os
from ...domain.orders.models import Order, OrderItem
from ...domain.orders.ports import OrderRepositoryPort
from ...domain.value_objects import Money, ProductId

def _order_to_dict(o: Order) -> dict:
    return {
        "id": str(o.id),
        "customer_id": str(o.customer_id),
        "is_submitted": o.is_submitted(),
        "items": [
            {
                "product_id": it.product_id.value,
                "unit_price": {"amount": it.unit_price.amount, "currency": it.unit_price.currency},
                "quantity": it.quantity,
            }
            for it in o.items()
        ],
    }

def _order_from_dict(d: dict) -> Order:
    o = Order(id=uuid.UUID(d["id"]), customer_id=uuid.UUID(d["customer_id"]))
    for it in d.get("items", []):
        o.add_item(ProductId(it["product_id"]), Money(it["unit_price"]["amount"], it["unit_price"]["currency"]), it["quantity"])
    if d.get("is_submitted"):
        # submit sets a flag and enforces invariants; since items exist it is safe:
        o.submit()
    return o

class FileOrderRepository(OrderRepositoryPort):
    def __init__(self, path: str):
        self.path = path
        if not os.path.exists(self.path):
            with open(self.path, "w") as f:
                json.dump({}, f)

    def _load(self) -> Dict[str, dict]:
        with open(self.path, "r") as f:
            return json.load(f)

    def _save_all(self, data: Dict[str, dict]) -> None:
        tmp = self.path + ".tmp"
        with open(tmp, "w") as f:
            json.dump(data, f)
        os.replace(tmp, self.path)

    def save(self, order: Order) -> None:
        data = self._load()
        data[str(order.id)] = _order_to_dict(order)
        self._save_all(data)

    def get(self, order_id: uuid.UUID) -> Optional[Order]:
        data = self._load()
        d = data.get(str(order_id))
        return _order_from_dict(d) if d else None

    def by_customer(self, customer_id: uuid.UUID) -> List[Order]:
        data = self._load()
        out: List[Order] = []
        for d in data.values():
            if d["customer_id"] == str(customer_id):
                out.append(_order_from_dict(d))
        return out
