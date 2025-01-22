import pytest
from typing import Dict, Any
from ..available_item import AvailableItem
from ..payment_provider import PaymentProvider
from ..item_type import ItemType

@pytest.fixture
def available_item() -> AvailableItem:
    return {
        "item_id": "test123",
        "item_name": "Test Item",
        "item_price": 10.0,
        "item_currency": "USD"
    }

def test_available_item_structure(available_item: AvailableItem) -> None:
    """Test AvailableItem structure."""
    assert available_item["item_id"] == "test123"
    assert available_item["item_name"] == "Test Item"
    assert available_item["item_price"] == pytest.approx(10.0)
    assert available_item["item_currency"] == "USD"

def test_payment_provider_values() -> None:
    """Test PaymentProvider enum values."""
    assert PaymentProvider.APPLE == "apple"
    assert PaymentProvider.GOOGLE == "google"
    assert PaymentProvider.PAYPAL == "paypal"
    assert PaymentProvider.COINBASE == "coinbase"
    assert PaymentProvider.COINSUB == "coinsub"

def test_item_type_values() -> None:
    """Test ItemType enum values."""
    assert ItemType.SUBSCRIPTION == "subscription"
    assert ItemType.ONE_TIME_PAYMENT == "one_time_payment"
    assert ItemType.UNKNOWN == "unknown" 