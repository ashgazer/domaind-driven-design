from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Optional
import uuid
from .models import Order

class OrderRepositoryPort(ABC):
    @abstractmethod
    def save(self, order: Order) -> None: ...
    @abstractmethod
    def get(self, order_id: uuid.UUID) -> Optional[Order]: ...
    @abstractmethod
    def by_customer(self, customer_id: uuid.UUID) -> List[Order]: ...
