# shop.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List
import uuid


# ========== Value Objects (immutable, no identity) ==========

@dataclass(frozen=True)
class Money:
    amount: int  # store smallest unit (pence/cents) to avoid float issues
    currency: str = "GBP"

    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Money cannot be negative")
        if not self.currency:
            raise ValueError("Currency is required")

    def add(self, other: "Money") -> "Money":
        _ensure_same_currency(self, other)
        return Money(self.amount + other.amount, self.currency)

    def multiply(self, qty: int) -> "Money":
        if qty <= 0:
            raise ValueError("Quantity must be positive")
        return Money(self.amount * qty, self.currency)


def _ensure_same_currency(a: Money, b: Money) -> None:
    if a.currency != b.currency:
        raise ValueError("Currency mismatch")


@dataclass(frozen=True)
class ProductId:
    value: str

    def __post_init__(self):
        if not self.value:
            raise ValueError("ProductId cannot be empty")


@dataclass(frozen=True)
class Email:
    value: str

    def __post_init__(self):
        if "@" not in self.value:
            raise ValueError("Invalid email address")


# ========== Entities (identity that persists) ==========

@dataclass
class Customer:
    id: uuid.UUID
    name: str
    email: Email

    @staticmethod
    def new(name: str, email: str) -> "Customer":
        return Customer(id=uuid.uuid4(), name=name, email=Email(email))


# ========== Aggregate (Order is the root) ==========

@dataclass(frozen=True)
class OrderItem:  # Typically a Value Object inside the Order aggregate
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

    # All modifications go through the aggregate root to enforce invariants
    def add_item(self, product_id: ProductId, unit_price: Money, quantity: int) -> None:
        self._assert_not_submitted()
        self._items.append(OrderItem(product_id, unit_price, quantity))

    def remove_item(self, product_id: ProductId) -> None:
        self._assert_not_submitted()
        self._items = [i for i in self._items if i.product_id != product_id]

    def total(self) -> Money:
        total = Money(0, "GBP")
        for i in self._items:
            _ensure_same_currency(total, i.unit_price)
            total = total.add(i.unit_price.multiply(i.quantity))
        return total

    def submit(self) -> None:
        self._assert_not_submitted()
        if not self._items:
            raise ValueError("Cannot submit an empty order")
        self._is_submitted = True

    def is_submitted(self) -> bool:
        return self._is_submitted

    def items(self) -> List[OrderItem]:
        # Expose a copy to preserve invariants
        return list(self._items)

    def _assert_not_submitted(self):
        if self._is_submitted:
            raise ValueError("Order is already submitted and cannot be modified")


# ========== Repository (in-memory) ==========

class OrderRepository:
    """Collection-like access to Orders, hiding storage details."""
    def __init__(self):
        self._store: Dict[uuid.UUID, Order] = {}

    def save(self, order: Order) -> None:
        self._store[order.id] = order

    def get(self, order_id: uuid.UUID) -> Order | None:
        return self._store.get(order_id)

    def by_customer(self, customer_id: uuid.UUID) -> List[Order]:
        return [o for o in self._store.values() if o.customer_id == customer_id]


# ========== Factory (to encapsulate creation complexity) ==========

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


# ========== Domain Service (logic that doesn't fit neatly on one entity) ==========

class DiscountService:
    """
    Example policy:
    - If a customer has >= 3 open (not submitted) orders, add a free bonus item to this order.
    - Or: apply 10% off if total exceeds a threshold (kept simple here).
    """

    BONUS_PRODUCT = ProductId("BONUS-STICKER")
    BONUS_PRICE = Money(0, "GBP")

    def maybe_apply_bulk_bonus(self, order: Order, orders_for_customer: List[Order]) -> None:
        open_count = sum(1 for o in orders_for_customer if not o.is_submitted())
        if open_count >= 3:
            # Add a freebie
            order.add_item(self.BONUS_PRODUCT, self.BONUS_PRICE, 1)

    def apply_threshold_discount(self, order: Order, threshold_pence: int, discount_pct: int) -> Order:
        """
        This returns a *new* Order reflecting a discount as an extra line.
        In a real system, you'd capture discounts differently. Kept simple & explicit here.
        """
        if discount_pct <= 0:
            return order

        current_total = order.total()
        if current_total.amount < threshold_pence:
            return order

        # Create a discount line as a negative price value object? We keep Money non-negative.
        # Instead, add a zero-priced "DISCOUNT" item and remember discount elsewhere is common,
        # but to *show* an effect, we can add a derived structure or recompute total externally.
        # For clarity, we’ll return a *computed total* so usage is obvious.
        # (Another approach: return the discounted Money directly.)
        return order  # Leave structure unchanged; caller can compute discounted total:

    @staticmethod
    def discounted_total(order: Order, discount_pct: int, threshold_pence: int) -> Money:
        total = order.total()
        if total.amount >= threshold_pence and discount_pct > 0:
            discount_amount = total.amount * discount_pct // 100
            return Money(total.amount - discount_amount, total.currency)
        return total


# ========== Application Service (orchestrates a use case) ==========

class CheckoutService:
    def __init__(self, repo: OrderRepository, discount_service: DiscountService):
        self.repo = repo
        self.discounts = discount_service

    def start_order_with_item(
        self, customer: Customer, product_id: str, unit_price_pence: int, quantity: int
    ) -> uuid.UUID:
        order = OrderFactory().create_with_first_item(
            customer_id=customer.id,
            product_id=product_id,
            unit_price_pence=unit_price_pence,
            quantity=quantity,
        )
        # domain policy that depends on other orders
        others = self.repo.by_customer(customer.id)
        self.discounts.maybe_apply_bulk_bonus(order, others)

        self.repo.save(order)
        return order.id

    def add_item(self, order_id: uuid.UUID, product_id: str, unit_price_pence: int, quantity: int) -> None:
        order = self.repo.get(order_id)
        if not order:
            raise ValueError("Order not found")
        order.add_item(ProductId(product_id), Money(unit_price_pence), quantity)
        self.repo.save(order)

    def preview_total_with_discount(self, order_id: uuid.UUID, threshold_pence: int, discount_pct: int) -> Money:
        order = self.repo.get(order_id)
        if not order:
            raise ValueError("Order not found")
        return DiscountService.discounted_total(order, discount_pct, threshold_pence)

    def submit(self, order_id: uuid.UUID) -> Money:
        order = self.repo.get(order_id)
        if not order:
            raise ValueError("Order not found")
        order.submit()
        self.repo.save(order)
        return order.total()


# ========== Demo (acts like a tiny test) ==========

def _pence(n: float) -> int:
    # helper to write Money in pounds more ergonomically in the demo
    return int(round(n * 100))

def demo():
    repo = OrderRepository()
    discounts = DiscountService()
    checkout = CheckoutService(repo, discounts)

    alice = Customer.new("Alice", "alice@example.com")

    # Start three orders to trigger the "bulk bonus" rule on the 3rd
    order1_id = checkout.start_order_with_item(alice, "TEA-BAG", _pence(2.50), 2)     # £5.00
    order2_id = checkout.start_order_with_item(alice, "MUG-RED", _pence(8.00), 1)      # £8.00
    order3_id = checkout.start_order_with_item(alice, "KETTLE", _pence(24.00), 1)      # £24.00 (+ free BONUS)

    order3 = repo.get(order3_id)
    print("Order 3 items:")
    for it in order3.items():
        print("-", it.product_id.value, "x", it.quantity, "@", f"{it.unit_price.amount/100:.2f}", it.unit_price.currency)

    print("Order 3 total:", f"£{order3.total().amount/100:.2f}")

    # Add another item to order 3
    checkout.add_item(order3_id, "TEA-BAG", _pence(2.50), 1)

    # Preview a discount (10% off if total >= £20)
    preview = checkout.preview_total_with_discount(order3_id, threshold_pence=_pence(20.0), discount_pct=10)
    print("Order 3 discounted preview (>= £20, 10% off):", f"£{preview.amount/100:.2f}")

    # Submit the order
    final_total = checkout.submit(order3_id)
    print("Order 3 submitted total:", f"£{final_total.amount/100:.2f}")

    # Trying to modify after submit should fail:
    try:
        checkout.add_item(order3_id, "SPOON", _pence(1.00), 1)
    except ValueError as e:
        print("Expected error after submit:", e)


if __name__ == "__main__":
    demo()

