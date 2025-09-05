
from dddshop.entities import Customer
from dddshop.orders.repository import OrderRepository
from dddshop.services.discounts import DiscountService
from dddshop.services.checkout import CheckoutService

def _pence(n: float) -> int:
    return int(round(n * 100))

def main():
    repo = OrderRepository()
    discounts = DiscountService()
    checkout = CheckoutService(repo, discounts)

    alice = Customer.new("Alice", "alice@example.com")

    order1 = checkout.start_order_with_item(alice, "TEA-BAG", _pence(2.50), 2)
    order2 = checkout.start_order_with_item(alice, "MUG-RED", _pence(8.00), 1)
    order3 = checkout.start_order_with_item(alice, "KETTLE", _pence(24.00), 1)

    checkout.add_item(order3, "TEA-BAG", _pence(2.50), 1)
    preview = checkout.preview_total_with_discount(order3, threshold_pence=_pence(20), discount_pct=10)
    print("Discounted preview:", f"£{preview.amount/100:.2f}")

    final_total = checkout.submit(order3)
    print("Final total:", f"£{final_total.amount/100:.2f}")

if __name__ == "__main__":
    main()
