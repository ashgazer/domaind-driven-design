from __future__ import annotations
from ...domain.entities import Customer
from ...domain.services.discounts import DiscountService
from ..persistence.in_memory_order_repository import InMemoryOrderRepository
from ...application.use_cases import CheckoutService

def _pence(n: float) -> int:
    return int(round(n * 100))

def main():
    repo = InMemoryOrderRepository()
    discounts = DiscountService()
    checkout = CheckoutService(repo, discounts)

    alice = Customer.new("Alice", "alice@example.com")

    # Two orders first
    checkout.start_order_with_item(alice, "TEA-BAG", _pence(2.50), 2)
    checkout.start_order_with_item(alice, "MUG-RED", _pence(8.00), 1)

    # Third triggers bonus
    order3 = checkout.start_order_with_item(alice, "KETTLE", _pence(24.00), 1)
    checkout.add_item(order3, "TEA-BAG", _pence(2.50), 1)

    preview = checkout.preview_total_with_discount(order3, threshold_pence=_pence(20), discount_pct=10)

    print("Order 3 discounted preview:", f"£{preview.amount/100:.2f}")
    final_total = checkout.submit(order3)
    print("Order 3 final total:", f"£{final_total.amount/100:.2f}")

if __name__ == "__main__":
    main()
