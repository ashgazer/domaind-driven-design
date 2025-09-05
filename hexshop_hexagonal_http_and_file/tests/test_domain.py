import uuid
from hexshop.domain.orders.models import Order
from hexshop.domain.value_objects import Money, ProductId

def _pence(n: float) -> int:
    return int(round(n * 100))

def test_order_total_and_submit():
    order = Order.new(uuid.uuid4())
    order.add_item(ProductId("P1"), Money(_pence(2.50)), 2)  # £5.00
    order.add_item(ProductId("P2"), Money(_pence(1.25)), 4)  # £5.00
    assert order.total().amount == _pence(10.00)

    order.submit()
    assert order.is_submitted()

    import pytest
    with pytest.raises(ValueError):
        order.add_item(ProductId("P3"), Money(_pence(1.00)), 1)
