import pytest
from ..item_type import ItemType

def test_item_type_values() -> None:
    """Test ItemType enum values."""
    assert ItemType.SUBSCRIPTION == "subscription"
    assert ItemType.ONE_TIME_PAYMENT == "one_time_payment"
    assert ItemType.UNKNOWN == "unknown"

def test_item_type_members() -> None:
    """Test ItemType enum members."""
    types = list(ItemType)
    assert len(types) == 3
    assert all(isinstance(t, ItemType) for t in types)

def test_item_type_from_string() -> None:
    """Test ItemType creation from string."""
    assert ItemType("subscription") == ItemType.SUBSCRIPTION
    assert ItemType("one_time_payment") == ItemType.ONE_TIME_PAYMENT
    assert ItemType("unknown") == ItemType.UNKNOWN 