from __future__ import annotations
from dataclasses import dataclass, field
from typing import List
import uuid
from ..value_objects import Money, ProductId, ensure_same_currency

@dataclass(frozen=True)
class OrderItem:
    product_id: ProductId
    unit_price: Money
    quantity: int

    def __post_init__(self):
        if self.quantity <= 0:
            raise ValueError("Quantity must be positive")

@dataclass
class Order:
    id: uuid.UUID
    customer_id: uuid.UUID
    _items: List[OrderItem] = field(default_factory=list)
    _is_submitted: bool = False

    @staticmethod
    def new(customer_id: uuid.UUID) -> "Order":
        return Order(id=uuid.uuid4(), customer_id=customer_id)

    def add_item(self, product_id: ProductId, unit_price: Money, quantity: int) -> None:
        self._assert_not_submitted()
        self._items.append(OrderItem(product_id, unit_price, quantity))

    def remove_item(self, product_id: ProductId) -> None:
        self._assert_not_submitted()
        self._items = [i for i in self._items if i.product_id != product_id]

    def items(self) -> List[OrderItem]:
        return list(self._items)

    def total(self) -> Money:
        total = Money(0, "GBP")
        for i in self._items:
            ensure_same_currency(total, i.unit_price)
            total = total.add(i.unit_price.multiply(i.quantity))
        return total

    def submit(self) -> None:
        self._assert_not_submitted()
        if not self._items:
            raise ValueError("Cannot submit an empty order")
        self._is_submitted = True

    def is_submitted(self) -> bool:
        return self._is_submitted

    def _assert_not_submitted(self):
        if self._is_submitted:
            raise ValueError("Order is already submitted and cannot be modified")
