
from __future__ import annotations
from .models import Order
from ..value_objects import ProductId, Money
import uuid

class OrderFactory:
    def create_with_first_item(
        self,
        customer_id: uuid.UUID,
        product_id: str,
        unit_price_pence: int,
        quantity: int,
        currency: str = "GBP",
    ) -> Order:
        order = Order.new(customer_id)
        order.add_item(ProductId(product_id), Money(unit_price_pence, currency), quantity)
        return order
