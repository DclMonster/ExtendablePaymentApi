import pytest
from typing import Dict, Any
from enum import StrEnum
from datetime import datetime
from ..payment_handler import PaymentHandler
from ..base_payment_data import BasePaymentData

class TestItemCategory(StrEnum):
    TEST_ITEM = "test_item"

class TestPaymentData(BasePaymentData[TestItemCategory], total=False):
    quantity: int

class TestPaymentHandler(PaymentHandler[TestItemCategory, TestPaymentData]):
    def onPayment(self, payment: TestPaymentData) -> None:
        print(payment)

@pytest.fixture
def payment_handler() -> TestPaymentHandler:
    return TestPaymentHandler(category=TestItemCategory.TEST_ITEM)

def test_payment_handler_process_payment(payment_handler: TestPaymentHandler) -> None:
    """Test processing a payment."""
    test_data: TestPaymentData = {
        "user_id": "test123",
        "item_name": "test_item",
        "purchase_id": "purchase123",
        "time_bought": "2024-01-19T00:00:00Z",
        "status": "paid",
        "item_category": TestItemCategory.TEST_ITEM
    }
    payment_handler.payment(test_data) 