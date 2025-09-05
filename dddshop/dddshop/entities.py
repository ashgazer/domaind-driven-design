
from __future__ import annotations
from dataclasses import dataclass
import uuid
from .value_objects import Email

@dataclass
class Customer:
    id: uuid.UUID
    name: str
    email: Email

    @staticmethod
    def new(name: str, email: str) -> "Customer":
        return Customer(id=uuid.uuid4(), name=name, email=Email(email))
