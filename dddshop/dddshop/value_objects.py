
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class Money:
    amount: int
    currency: str = "GBP"

    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Money cannot be negative")
        if not self.currency:
            raise ValueError("Currency is required")

    def add(self, other: "Money") -> "Money":
        ensure_same_currency(self, other)
        return Money(self.amount + other.amount, self.currency)

    def multiply(self, qty: int) -> "Money":
        if qty <= 0:
            raise ValueError("Quantity must be positive")
        return Money(self.amount * qty, self.currency)


def ensure_same_currency(a: "Money", b: "Money") -> None:
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
