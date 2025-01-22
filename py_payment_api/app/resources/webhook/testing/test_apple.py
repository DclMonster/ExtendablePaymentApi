import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import math
from ....services import PaymentProvider
from ....services.store.enum.item_type import ItemType
from ..apple import AppleWebhook, AppleWebhookError, AppleWebhookData
from ....services.forwarder.abstract.forwarder import Forwarder, ForwarderType
from ....services.store.payment.one_time.one_time_payment_data import OneTimePaymentData
from ....services.store.payment.subscription.subscription_payment_data import SubscriptionPaymentData
from typing import Dict, Any, TypedDict, cast, Literal

@pytest.fixture
def mock_forwarder() -> Forwarder:
    return Mock(spec=Forwarder)

@pytest.fixture
def apple_webhook(mock_forwarder: Forwarder) -> AppleWebhook[ItemType]:
    return AppleWebhook[ItemType](forwarder=mock_forwarder)

def test_parse_event_data_success(apple_webhook: AppleWebhook[ItemType]) -> None:
    event_data = '''
    {
        "notification_type": "DID_RENEW",
        "unified_receipt": {
            "environment": "Production",
            "latest_receipt_info": [{
                "transaction_id": "tx123",
                "product_id": "com.example.item1",
                "purchase_date_ms": "1634567890000",
                "quantity": "1",
                "in_app_ownership_type": "PURCHASED",
                "price": "10.99",
                "currency": "USD"
            }],
            "status": 0
        },
        "auto_renew_status": "true",
        "auto_renew_product_id": "com.example.item1",
        "environment": "Production",
        "user_id": "user123"
    }
    '''
    
    result = apple_webhook.parse_event_data(event_data)
    
    assert result['transaction_id'] == 'tx123'
    assert math.isclose(result['amount'], 10.99, rel_tol=1e-9)
    assert result['currency'] == 'USD'
    assert result['status'] == 'paid'
    assert result['user_id'] == 'user123'

def test_parse_event_data_missing_fields(apple_webhook: AppleWebhook[ItemType]) -> None:
    event_data = '''
    {
        "notification_type": "DID_RENEW",
        "unified_receipt": {
            "environment": "Production",
            "latest_receipt_info": [{
                "product_id": "com.example.item1"
            }]
        }
    }
    '''
    
    with pytest.raises(AppleWebhookError, match="Missing required fields: transaction_id"):
        apple_webhook.parse_event_data(event_data)

def test_parse_event_data_invalid_json(apple_webhook: AppleWebhook[ItemType]) -> None:
    event_data = 'invalid json'
    
    with pytest.raises(AppleWebhookError, match="Error parsing event data"):
        apple_webhook.parse_event_data(event_data)

def test_map_status(apple_webhook: AppleWebhook[ItemType]) -> None:
    assert apple_webhook._map_status('INITIAL_BUY', '') == 'paid'
    assert apple_webhook._map_status('DID_RENEW', '') == 'paid'
    assert apple_webhook._map_status('DID_FAIL_TO_RENEW', '') == 'webhook_recieved'
    assert apple_webhook._map_status('CANCEL', '') == 'sent_to_processor'
    assert apple_webhook._map_status('UNKNOWN', '') == 'webhook_recieved'

def test_get_one_time_payment_data(apple_webhook: AppleWebhook[ItemType]) -> None:
    event_data: AppleWebhookData = {
        'transaction_id': 'tx123',
        'amount': 10.99,
        'currency': 'USD',
        'status': 'paid',
        'user_id': 'user123'
    }
    
    result = apple_webhook._get_one_time_payment_data(event_data)
    
    assert result['user_id'] == 'user123'
    assert result['item_category'] == ItemType.ONE_TIME_PAYMENT
    assert result['purchase_id'] == 'tx123'
    assert result['status'] == 'paid'
    assert result['quantity'] == 1

def test_get_subscription_payment_data(apple_webhook: AppleWebhook[ItemType]) -> None:
    event_data: AppleWebhookData = {
        'transaction_id': 'tx123',
        'amount': 10.99,
        'currency': 'USD',
        'status': 'paid',
        'user_id': 'user123',
        'subscription_id': 'sub123'
    }
    
    result = apple_webhook._get_subscription_payment_data(event_data)
    
    assert result['user_id'] == 'user123'
    assert result['item_category'] == ItemType.SUBSCRIPTION
    assert result['purchase_id'] == 'tx123'
    assert result['status'] == 'paid'

@patch('builtins.print')
def test_post_event(mock_print: MagicMock, apple_webhook: AppleWebhook[ItemType]) -> None:
    event_data = {
        'notification_type': 'DID_RENEW',
        'unified_receipt': {
            'latest_receipt_info': [{
                'transaction_id': 'tx123',
                'product_id': 'com.example.item1',
                'price': '10.99',
                'currency': 'USD'
            }]
        }
    }
    
    with patch('flask.request') as mock_request:
        mock_request.get_json.return_value = event_data
        mock_request.headers = {'X-Apple-Signature': 'valid_signature'}
        
        response = apple_webhook.post()
        
        assert response.status_code == 200
        mock_print.assert_called_with('Subscription renewed:', event_data) 