
from __future__ import annotations
from ..orders.models import Order
from ..value_objects import Money, ProductId

class DiscountService:
    BONUS_PRODUCT = ProductId("BONUS-STICKER")
    BONUS_PRICE = Money(0, "GBP")

    def maybe_apply_bulk_bonus(self, order: Order, orders_for_customer: list[Order]) -> None:
        open_count = sum(1 for o in orders_for_customer if not o.is_submitted())
        if open_count >= 3:
            order.add_item(self.BONUS_PRODUCT, self.BONUS_PRICE, 1)

    @staticmethod
    def discounted_total(order: Order, discount_pct: int, threshold_pence: int) -> Money:
        total = order.total()
        if total.amount >= threshold_pence and discount_pct > 0:
            discount_amount = total.amount * discount_pct // 100
            return Money(total.amount - discount_amount, total.currency)
        return total
