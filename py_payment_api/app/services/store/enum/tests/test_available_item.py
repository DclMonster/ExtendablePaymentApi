import pytest
from ....testing.app import client
from ..available_item import AvailableItem

# Example test case for AvailableItem
@pytest.fixture
def available_item():
    return AvailableItem(name='Test Item', price=10.0)

# Example test case for item name
def test_available_item_name(available_item):
    assert available_item.name == 'Test Item'

# Example test case for item price
def test_available_item_price(available_item):
    assert available_item.price == 10.0 