# HexShop — Hexagonal (Ports & Adapters) Example

This is the evolution of the in-memory DDD mini-project into a **Hexagonal Architecture** (aka **Ports & Adapters**).  
The **domain** is pure. The **application** layer orchestrates use-cases via **ports** (interfaces). **Adapters** implement those ports (here: in-memory). A CLI adapter is provided.

## Layout

```
hexshop/
  domain/
    value_objects.py, entities.py
    orders/models.py, orders/ports.py
    services/discounts.py
  application/
    use_cases.py
  infrastructure/
    persistence/in_memory_order_repository.py
    cli/main.py
tests/
  test_domain.py
  test_application.py
Makefile
```

## Run

```bash
python -m pip install -U pytest
make test
make demo   # runs the CLI demo
```

## Notes

- The domain layer has **no imports** from application or infrastructure.
- The application layer depends **only** on domain and its ports.
- Infrastructure implements ports and wires everything together.
