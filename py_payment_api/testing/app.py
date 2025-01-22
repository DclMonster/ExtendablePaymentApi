"""Test application configuration and fixtures."""
import pytest
from flask import Flask
from flask.testing import FlaskClient
from typing import Generator, Any, Dict
from ..app.config import configure_creditor, configure_webhook
from ..app import PaymentProvider
from ..app.services import init_services, ItemType
from ..app.services.store.payment.abstract import ItemCollectionService
from ..app.services.store.payment.subscription import SubscriptionPaymentHandler
from ..app.services.store.payment.one_time import OneTimePaymentHandler
from ..app.services.forwarder.restful_forwarder import RestfulForwarder
from enum import StrEnum

class TestItemCategory(StrEnum):
    TEST_ITEM = "test_item"

class TestItemCollectionService(ItemCollectionService[TestItemCategory]):
    order_status_changes: Dict[str, str] = {}
    def __init__(self) -> None:
        super().__init__("test_collection", ItemType.ONE_TIME_PAYMENT)

    def change_order_status(self, purchase_id: str, status: str) -> None:
        self.order_status_changes[purchase_id] = status

def create_test_app() -> Flask:
    """Create and configure a test Flask application."""
    app = Flask(__name__)
    app.config.update({
        'TESTING': True,
        'DEBUG': True,
        'SERVER_NAME': 'localhost'
    })

    # Initialize services
    item_service = TestItemCollectionService()
    item_type_to_service: Dict[ItemType, ItemCollectionService[TestItemCategory]] = {
        ItemType.ONE_TIME_PAYMENT: item_service,
        ItemType.SUBSCRIPTION: item_service
    }
    sub_handlers: Dict[TestItemCategory, SubscriptionPaymentHandler[TestItemCategory, Any]] = {
        TestItemCategory.TEST_ITEM: SubscriptionPaymentHandler(TestItemCategory.TEST_ITEM, item_service)
    }
    one_time_handlers: Dict[TestItemCategory, OneTimePaymentHandler[TestItemCategory, Any]] = {
        TestItemCategory.TEST_ITEM: OneTimePaymentHandler(TestItemCategory.TEST_ITEM, item_service)
    }

    init_services([PaymentProvider.PAYPAL], item_type_to_service, sub_handlers, one_time_handlers)

    configure_creditor(app)
    forwarder = RestfulForwarder(url="http://test-endpoint.com")
    configure_webhook(app, [PaymentProvider.PAYPAL], forwarder)
    return app

# Create a test app instance
app = create_test_app()