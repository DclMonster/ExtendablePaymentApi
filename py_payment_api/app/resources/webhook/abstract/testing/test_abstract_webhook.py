import pytest
from dataclasses import dataclass
from enum import StrEnum
from unittest.mock import Mock, patch
from .....services import PaymentProvider, ItemType
from ..abstract_webhook import AbstractWebhook
from .....services.store.payment.one_time.one_time_payment_data import OneTimePaymentData
from .....services.store.payment.subscription.subscription_payment_data import SubscriptionPaymentData
from .....services import PurchaseStatus
from datetime import datetime
from typing import Generator

class TestItemCategory(StrEnum):
    TEST = "test"

@dataclass
class TestProviderData:
    item_name: str
    amount: float

class TestWebhook(AbstractWebhook[TestProviderData, TestItemCategory]):
    def _get_one_time_payment_data(self, event_data: TestProviderData) -> OneTimePaymentData[TestItemCategory]:
        return OneTimePaymentData(
            item_name=event_data.item_name,
            quantity=int(event_data.amount),
            purchase_id="test123",
            user_id="test123",
            time_bought=datetime.now().isoformat(),
            status=PurchaseStatus.SENT_TO_WEBSOCKET.value,
            item_category=TestItemCategory.TEST
        )

    def _get_subscription_payment_data(self, event_data: TestProviderData) -> SubscriptionPaymentData[TestItemCategory]:
        return SubscriptionPaymentData(
            item_name=event_data.item_name,
            item_category=TestItemCategory.TEST,
            purchase_id="test123",
            user_id="test123",
            time_bought=datetime.now().isoformat(),
            status=PurchaseStatus.SENT_TO_WEBSOCKET.value
        )

    def _item_name_provider(self, event_data: TestProviderData) -> str:
        return event_data.item_name

    def parse_event_data(self, event_data: str) -> TestProviderData:
        return TestProviderData(item_name="test_item", amount=10.0)

@pytest.fixture
def webhook() -> TestWebhook:
    verifier = Mock()
    return TestWebhook(
        provider_type=PaymentProvider.PAYPAL,
        verifier=verifier,
        forwarder=None
    )

@pytest.fixture
def webhook_with_forwarder() -> TestWebhook:
    verifier = Mock()
    forwarder = Mock()
    return TestWebhook(
        provider_type=PaymentProvider.PAYPAL,
        verifier=verifier,
        forwarder=forwarder
    )

@pytest.fixture
def mock_request() -> Generator[Mock, None, None]:
    with patch('py_payment_api.app.resources.webhook.abstract.abstract_webhook.request') as mock:
        mock.get_data.return_value = "test_data"
        mock.headers = {"X-Signature": "test_signature"}
        yield mock

@pytest.fixture
def mock_services() -> Generator[Mock, None, None]:
    with patch('py_payment_api.app.resources.webhook.abstract.abstract_webhook.get_services') as mock_get_services:
        services = Mock()
        mock_get_services.return_value = services
        yield services

def test_post_one_time_payment(webhook: TestWebhook, mock_request: Mock, mock_services: Mock) -> None:
    # Arrange
    mock_services.get_purchase_type.return_value = ItemType.ONE_TIME_PAYMENT
    
    # Act
    response = webhook.post()

    # Assert
    webhook._AbstractWebhook__verifier.verify_header_signature.assert_called_once()
    mock_services._handle_one_time_payment.assert_called_once()
    assert response.status_code == 200

def test_post_subscription(webhook: TestWebhook, mock_request: Mock, mock_services: Mock) -> None:
    # Arrange
    mock_services.get_purchase_type.return_value = ItemType.SUBSCRIPTION
    
    # Act
    response = webhook.post()

    # Assert
    webhook._AbstractWebhook__verifier.verify_header_signature.assert_called_once()
    mock_services._handle_subscription.assert_called_once()
    assert response.status_code == 200

def test_post_with_forwarder(webhook_with_forwarder: TestWebhook, mock_request: Mock, mock_services: Mock) -> None:
    # Act
    response = webhook_with_forwarder.post()

    # Assert
    webhook_with_forwarder._AbstractWebhook__verifier.verify_header_signature.assert_called_once()
    webhook_with_forwarder._AbstractWebhook__forwarder.forward_event.assert_called_once()
    assert response.status_code == 200

def test_post_unknown_item_type(webhook: TestWebhook, mock_request: Mock, mock_services: Mock) -> None:
    # Arrange
    mock_services.get_purchase_type.return_value = ItemType.UNKNOWN
    
    # Act & Assert
    with pytest.raises(ValueError, match="Unknown item purchase type:"):
        webhook.post() 