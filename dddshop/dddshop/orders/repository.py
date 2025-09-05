
from __future__ import annotations
from typing import Dict, List, Optional
import uuid
from .models import Order

class OrderRepository:
    def __init__(self):
        self._store: Dict[uuid.UUID, Order] = {}

    def save(self, order: Order) -> None:
        self._store[order.id] = order

    def get(self, order_id: uuid.UUID) -> Optional[Order]:
        return self._store.get(order_id)

    def by_customer(self, customer_id: uuid.UUID) -> List[Order]:
        return [o for o in self._store.values() if o.customer_id == customer_id]
