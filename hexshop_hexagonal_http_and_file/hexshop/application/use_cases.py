from __future__ import annotations
import uuid
from ..domain.entities import Customer
from ..domain.orders.models import Order
from ..domain.orders.ports import OrderRepositoryPort
from ..domain.value_objects import ProductId, Money
from ..domain.services.discounts import DiscountService

class CheckoutService:
    def __init__(self, repo: OrderRepositoryPort, discounts: DiscountService):
        self.repo = repo
        self.discounts = discounts

    def start_order_with_item(self, customer: Customer, product_id: str, unit_price_pence: int, quantity: int) -> uuid.UUID:
        order = Order.new(customer.id)
        order.add_item(ProductId(product_id), Money(unit_price_pence), quantity)
        others = self.repo.by_customer(customer.id)
        self.discounts.maybe_apply_bulk_bonus(order, others)
        self.repo.save(order)
        return order.id

    def add_item(self, order_id: uuid.UUID, product_id: str, unit_price_pence: int, quantity: int) -> None:
        order = self._get_or_raise(order_id)
        order.add_item(ProductId(product_id), Money(unit_price_pence), quantity)
        self.repo.save(order)

    def preview_total_with_discount(self, order_id: uuid.UUID, threshold_pence: int, discount_pct: int):
        order = self._get_or_raise(order_id)
        return DiscountService.discounted_total(order, discount_pct, threshold_pence)

    def submit(self, order_id: uuid.UUID):
        order = self._get_or_raise(order_id)
        order.submit()
        self.repo.save(order)
        return order.total()

    def _get_or_raise(self, order_id: uuid.UUID):
        order = self.repo.get(order_id)
        if not order:
            raise ValueError("Order not found")
        return order
