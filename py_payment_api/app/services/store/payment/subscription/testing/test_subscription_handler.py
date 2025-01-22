import pytest
from typing import Dict, Any
from enum import StrEnum
from datetime import datetime
from ..subscription_payment_data import SubscriptionPaymentData
from ..subscription_payment_handler import SubscriptionPaymentHandler
from ...abstract.payment_handler import PaymentException

class MockItemCategory(StrEnum):
    ITEM_CATEGORY = "item_category"

@pytest.fixture
def subscription_handler() -> SubscriptionPaymentHandler[MockItemCategory, SubscriptionPaymentData[MockItemCategory]]:
    """Create a subscription handler for testing."""
    return SubscriptionPaymentHandler[MockItemCategory, SubscriptionPaymentData[MockItemCategory]](category=MockItemCategory.ITEM_CATEGORY)

def create_mock_data() -> Dict[str, Any]:
    """Create mock payment data for testing."""
    return {
        "purchase_id": "1",
        "user_id": "1",
        "item_name": "test_item",
        "time_bought": datetime.now().isoformat(),
        "status": "paid",
        "item_category": MockItemCategory.ITEM_CATEGORY
    }

def test_subscription_handler_handle_subscription_success(
    subscription_handler: SubscriptionPaymentHandler[MockItemCategory, SubscriptionPaymentData[MockItemCategory]]
) -> None:
    """Test successful subscription payment handling."""
    result = subscription_handler.payment(SubscriptionPaymentData(
        purchase_id="1",
        user_id="1",
        item_name="test_item",
        time_bought=datetime.now().isoformat(),
        status="paid",
        item_category=MockItemCategory.ITEM_CATEGORY
    )) 
    assert result is True

def test_subscription_handler_handle_subscription_invalid_status(
    subscription_handler: SubscriptionPaymentHandler[MockItemCategory, SubscriptionPaymentData[MockItemCategory]]
) -> None:
    """Test subscription payment handling with invalid status."""
    result = subscription_handler.payment(SubscriptionPaymentData(
        purchase_id="1",
        user_id="1",
        item_name="test_item",
        time_bought=datetime.now().isoformat(),
        status="webhook_recieved",
        item_category=MockItemCategory.ITEM_CATEGORY
    )) 
    assert result is False

def test_subscription_handler_handle_subscription_missing_data(
    subscription_handler: SubscriptionPaymentHandler[MockItemCategory, SubscriptionPaymentData[MockItemCategory]]
) -> None:
    """Test subscription payment handling with missing data."""
    with pytest.raises(PaymentException):
        subscription_handler.payment(None)  # type: ignore