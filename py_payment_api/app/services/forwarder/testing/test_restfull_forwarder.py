import pytest
from typing import Dict, Any
from unittest.mock import patch, MagicMock
from enum import StrEnum
from ..restful_forwarder import RestfulForwarder
from ....services import StoreServiceError
from ....services import init_services, get_services
from ....services import PaymentProvider, ItemType, ItemCollectionService, PurchaseStatus, PurchaseDetail
from datetime import datetime
class TestEventType(StrEnum):
    PAYMENT_COMPLETED = "payment.completed"
    PAYMENT_FAILED = "payment.failed"



@pytest.fixture
def restful_forwarder() -> RestfulForwarder:
    item_collection_service: ItemCollectionService[Any] = ItemCollectionService(collection_name="test", item_type=ItemType.ONE_TIME_PAYMENT)
    item_collection_service.log_webhook_recieved(PurchaseDetail(
        purchase_id="test456",
        item_id="test123",
        user_id="test123",
        time_bought=datetime.now()
    ))
    init_services(
        enabled_providers=[PaymentProvider.APPLE],
        item_type_to_item_service={
            ItemType.ONE_TIME_PAYMENT: item_collection_service
        },
        sub_handlers={},
        one_time_handlers={}
    )
    return RestfulForwarder(url="http://test-endpoint.com")

@patch('requests.post')
def test_restful_forwarder_forward_success(
    mock_post: MagicMock,
    restful_forwarder: RestfulForwarder
) -> None:
    """Test successful forwarding of data via REST."""
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"status": "success"}

    test_data: Dict[str, Any] = {
        "event": TestEventType.PAYMENT_COMPLETED,
        "data": {
            "payment_id": "test123",
            "amount": 100
        }
    }

    restful_forwarder.forward_event(test_data)
    mock_post.assert_called_once_with(
        "http://test-endpoint.com",
        json=test_data,
        headers={"Content-Type": "application/json"})

def test_restful_forwarder_fails_with_unknown_purchase_id(restful_forwarder: RestfulForwarder) -> None:
    """Test failed forwarding of data via REST."""
    test_data: Dict[str, Any] = {
        "event": TestEventType.PAYMENT_COMPLETED,
        "data": {
            "purchase_id": "test123",
            "amount": 100
        }
    }
    with pytest.raises(StoreServiceError):
        restful_forwarder.forward_event(test_data)

@patch('requests.post')
def test_restful_forwarder_forward_failure(
    mock_post: MagicMock,
    restful_forwarder: RestfulForwarder
) -> None:
    """Test failed forwarding of data via REST."""
    mock_post.return_value.status_code = 500
    mock_post.return_value.json.return_value = {"status": "error"}

    test_data: Dict[str, Any] = {
        "order_id": "test456",
    }

    restful_forwarder.forward_event(test_data)
    mock_post.assert_called_once_with("http://test-endpoint.com/creditor_api", json=test_data, headers={"Content-Type": "application/json"})
