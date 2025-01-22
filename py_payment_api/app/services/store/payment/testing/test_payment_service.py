import pytest
from typing import Dict, Any, TypedDict, cast
from enum import StrEnum
from ..payment_service import PaymentService
from ...enum.payment_provider import PaymentProvider
from ..one_time import OneTimePaymentHandler, OneTimePaymentData

class TestItemCategory(StrEnum):
    TEST_ITEM = "test_item"

class IncompletePaymentData(TypedDict):
    user_id: str
    item_name: str
    purchase_id: str
    time_bought: str
    status: str

@pytest.fixture
def payment_service() -> PaymentService[TestItemCategory, TestItemCategory]:
    return PaymentService[TestItemCategory, TestItemCategory](enabled_providers=[
        PaymentProvider.PAYPAL,
        PaymentProvider.GOOGLE,
        PaymentProvider.COINBASE,
        PaymentProvider.APPLE,
        PaymentProvider.COINSUB
    ])

def test_payment_service_handle_payment_no_handlers(
    payment_service: PaymentService[TestItemCategory, TestItemCategory]
) -> None:
    """Test handling a payment with no handlers registered."""
    test_data: OneTimePaymentData[TestItemCategory] = {
        "user_id": "test123",
        "item_name": "test_item",
        "purchase_id": "purchase123",
        "time_bought": "2024-01-19T00:00:00Z",
        "status": "paid",
        "item_category": TestItemCategory.TEST_ITEM,
        "quantity": 1
    }
    with pytest.raises(Exception):  # Should raise since no handlers are registered
        payment_service.handle_one_time_payment(
            provider=PaymentProvider.PAYPAL,
            category=TestItemCategory.TEST_ITEM,
            data=test_data
        )

def test_payment_service_handle_payment_with_handler(
    payment_service: PaymentService[TestItemCategory, TestItemCategory]
) -> None:
    """Test handling a payment with a handler registered."""
    class MockHandler(OneTimePaymentHandler[TestItemCategory, OneTimePaymentData[TestItemCategory]]):
        def onPayment(self, payment: OneTimePaymentData[TestItemCategory]) -> None:
            assert payment["user_id"] == "test123"
            assert payment["item_name"] == "test_item"
            assert payment["purchase_id"] == "purchase123"
            assert payment["time_bought"] == "2024-01-19T00:00:00Z"
            assert payment["status"] == "paid"
            assert payment["item_category"] == TestItemCategory.TEST_ITEM
            assert payment["quantity"] == 1

    # Register the mock handler
    mock_handler = MockHandler(category=TestItemCategory.TEST_ITEM)
    payment_service.register_one_time_handler(TestItemCategory.TEST_ITEM, mock_handler)

    # This should not raise an exception
    test_data: OneTimePaymentData[TestItemCategory] = {
        "user_id": "test123",
        "item_name": "test_item",
        "purchase_id": "purchase123",
        "time_bought": "2024-01-19T00:00:00Z",
        "status": "paid",
        "item_category": TestItemCategory.TEST_ITEM,
        "quantity": 1
    }
    payment_service.handle_one_time_payment(
        provider=PaymentProvider.PAYPAL,
        category=TestItemCategory.TEST_ITEM,
        data=test_data
    )

def test_payment_service_handle_payment_missing_fields(
    payment_service: PaymentService[TestItemCategory, TestItemCategory]
) -> None:
    """Test handling a payment with missing required fields."""
    incomplete_data: IncompletePaymentData = {
        "user_id": "test123",
        "item_name": "test_item",
        "purchase_id": "purchase123",
        "time_bought": "2024-01-19T00:00:00Z",
        "status": "paid"
    }
    with pytest.raises(KeyError):  # Assuming KeyError is raised for missing fields
        payment_service.handle_one_time_payment(
            provider=PaymentProvider.PAYPAL,
            category=TestItemCategory.TEST_ITEM,
            data=cast(OneTimePaymentData[TestItemCategory], incomplete_data)
        )