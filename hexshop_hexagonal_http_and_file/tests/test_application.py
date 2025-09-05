from hexshop.domain.entities import Customer
from hexshop.domain.services.discounts import DiscountService
from hexshop.infrastructure.persistence.in_memory_order_repository import InMemoryOrderRepository
from hexshop.application.use_cases import CheckoutService

def _pence(n: float) -> int:
    return int(round(n * 100))

def test_checkout_with_bonus_and_discount():
    repo = InMemoryOrderRepository()
    discounts = DiscountService()
    checkout = CheckoutService(repo, discounts)

    alice = Customer.new("Alice", "alice@example.com")
    checkout.start_order_with_item(alice, "TEA-BAG", _pence(2.50), 2)
    checkout.start_order_with_item(alice, "MUG-RED", _pence(8.00), 1)
    third = checkout.start_order_with_item(alice, "KETTLE", _pence(24.00), 1)

    checkout.add_item(third, "TEA-BAG", _pence(2.50), 1)
    preview = checkout.preview_total_with_discount(third, threshold_pence=_pence(20), discount_pct=10)
    assert preview.amount > 0

    total = checkout.submit(third)
    assert total.amount >= preview.amount
