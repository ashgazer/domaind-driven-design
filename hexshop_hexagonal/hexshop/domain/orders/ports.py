from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Optional
import uuid
from .models import Order

class OrderRepositoryPort(ABC):
    """Port defining the behavior the application needs from an order repository."""
    @abstractmethod
    def save(self, order: Order) -> None: ...
    @abstractmethod
    def get(self, order_id: uuid.UUID) -> Optional[Order]: ...
    @abstractmethod
    def by_customer(self, customer_id: uuid.UUID) -> List[Order]: ...
