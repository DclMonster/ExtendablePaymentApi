import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from ....services import PaymentProvider
from ....services.store.enum.item_type import ItemType
from ..coinsub import CoinSubWebhook, CoinSubWebhookError, CoinSubWebhookData
from ....services.forwarder.abstract.forwarder import Forwarder, ForwarderType
from ....services.store.payment.one_time.one_time_payment_data import OneTimePaymentData
from ....services.store.payment.subscription.subscription_payment_data import SubscriptionPaymentData
from typing import Dict, Any, TypedDict, cast, Literal

class TestEventData(TypedDict):
    transaction_id: str
    amount: float
    currency: str
    status: str
    user_id: str
    subscription_id: str

@pytest.fixture
def mock_forwarder() -> Forwarder:
    return Mock(spec=Forwarder)

@pytest.fixture
def coinsub_webhook(mock_forwarder: Forwarder) -> CoinSubWebhook[ItemType]:
    return CoinSubWebhook[ItemType](forwarder=mock_forwarder)

def test_parse_event_data_success(coinsub_webhook: CoinSubWebhook[ItemType]) -> None:
    event_data = '''
    {
        "event_type": "subscription_activated",
        "subscription": {
            "transaction_id": "tx123",
            "amount": 10.99,
            "currency": "USD",
            "status": "active",
            "user_id": "user123",
            "subscription_id": "sub123"
        }
    }
    '''
    
    result = coinsub_webhook.parse_event_data(event_data)
    
    assert result['transaction_id'] == 'tx123'
    assert isinstance(result['amount'], float)
    assert result['currency'] == 'USD'
    assert result['status'] == 'paid'
    assert result['user_id'] == 'user123'
    assert result['subscription_id'] == 'sub123'

def test_parse_event_data_missing_fields(coinsub_webhook: CoinSubWebhook[ItemType]) -> None:
    event_data = '''
    {
        "event_type": "subscription_activated",
        "subscription": {
            "amount": 10.99,
            "currency": "USD"
        }
    }
    '''
    
    with pytest.raises(CoinSubWebhookError, match="Missing required fields: transaction_id, status"):
        coinsub_webhook.parse_event_data(event_data)

def test_parse_event_data_invalid_json(coinsub_webhook: CoinSubWebhook[ItemType]) -> None:
    event_data = 'invalid json'
    
    with pytest.raises(CoinSubWebhookError, match="Error parsing event data"):
        coinsub_webhook.parse_event_data(event_data)

def test_map_status(coinsub_webhook: CoinSubWebhook[ItemType]) -> None:
    assert coinsub_webhook._map_status('subscription_created', '') == 'webhook_recieved'
    assert coinsub_webhook._map_status('subscription_activated', '') == 'paid'
    assert coinsub_webhook._map_status('subscription_canceled', '') == 'sent_to_processor'
    assert coinsub_webhook._map_status('subscription_renewed', '') == 'paid'
    assert coinsub_webhook._map_status('subscription_failed', '') == 'webhook_recieved'
    assert coinsub_webhook._map_status('subscription_expired', '') == 'sent_to_processor'
    assert coinsub_webhook._map_status('unknown_event', '') == 'webhook_recieved'

def test_get_one_time_payment_data(coinsub_webhook: CoinSubWebhook[ItemType]) -> None:
    event_data: CoinSubWebhookData = {
        'transaction_id': 'tx123',
        'amount': 10.99,
        'currency': 'USD',
        'status': 'paid',
        'user_id': 'user123',
        'subscription_id': 'sub123'
    }
    
    result = coinsub_webhook._get_one_time_payment_data(event_data)
    
    assert result['user_id'] == 'user123'
    assert result['item_category'] == ItemType.ONE_TIME_PAYMENT
    assert result['purchase_id'] == 'tx123'
    assert result['item_name'] == 'sub123'
    assert result['status'] == 'paid'
    assert result['quantity'] == 1

def test_get_subscription_payment_data(coinsub_webhook: CoinSubWebhook[ItemType]) -> None:
    event_data: CoinSubWebhookData = {
        'transaction_id': 'tx123',
        'amount': 10.99,
        'currency': 'USD',
        'status': 'paid',
        'user_id': 'user123',
        'subscription_id': 'sub123'
    }
    
    result = coinsub_webhook._get_subscription_payment_data(event_data)
    
    assert result['user_id'] == 'user123'
    assert result['item_category'] == ItemType.SUBSCRIPTION
    assert result['purchase_id'] == 'tx123'
    assert result['item_name'] == 'sub123'
    assert result['status'] == 'paid'

@patch('builtins.print')
def test_process_event(mock_print: MagicMock, coinsub_webhook: CoinSubWebhook[ItemType]) -> None:
    event_data = {
        'event_type': 'subscription_activated',
        'subscription': {
            'transaction_id': 'tx123'
        }
    }
    
    coinsub_webhook.process_event(event_data, False)
    
    mock_print.assert_called_with('Subscription activated:', event_data)
