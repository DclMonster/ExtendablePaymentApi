import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from ....services import PaymentProvider
from ....services.store.enum.item_type import ItemType
from ..coinbase import CoinbaseWebhook, CoinbaseWebhookError, CoinbaseWebhookData
from ....services.forwarder.abstract.forwarder import Forwarder, ForwarderType
from ....services.store.payment.one_time.one_time_payment_data import OneTimePaymentData
from typing import Dict, Any, TypedDict, cast, Literal
import math

@pytest.fixture
def mock_forwarder() -> Forwarder:
    return Mock(spec=Forwarder)

@pytest.fixture
def coinbase_webhook(mock_forwarder: Forwarder) -> CoinbaseWebhook[ItemType]:
    return CoinbaseWebhook[ItemType](forwarder=mock_forwarder)

def test_parse_event_data_success(coinbase_webhook: CoinbaseWebhook[ItemType]) -> None:
    event_data = '''
    {
        "event": {
            "type": "charge:confirmed",
            "data": {
                "code": "tx123",
                "pricing": {
                    "local": {
                        "amount": "10.99",
                        "currency": "USD"
                    }
                },
                "metadata": {
                    "user_id": "user123"
                },
                "timeline": [
                    {
                        "status": "completed"
                    }
                ]
            }
        }
    }
    '''
    
    result = coinbase_webhook.parse_event_data(event_data)
    
    assert result['transaction_id'] == 'tx123'
    assert isinstance(result['amount'], float)
    assert math.isclose(result['amount'], 10.99, rel_tol=1e-9)
    assert result['currency'] == 'USD'
    assert result['status'] == 'paid'
    assert result['user_id'] == 'user123'

def test_parse_event_data_missing_fields(coinbase_webhook: CoinbaseWebhook[ItemType]) -> None:
    event_data = '''
    {
        "event": {
            "type": "charge:confirmed",
            "data": {
                "pricing": {
                    "local": {
                        "amount": "10.99",
                        "currency": "USD"
                    }
                }
            }
        }
    }
    '''
    
    with pytest.raises(CoinbaseWebhookError, match="Missing required fields: transaction_id, status"):
        coinbase_webhook.parse_event_data(event_data)

def test_parse_event_data_invalid_json(coinbase_webhook: CoinbaseWebhook[ItemType]) -> None:
    event_data = 'invalid json'
    
    with pytest.raises(CoinbaseWebhookError, match="Error parsing event data"):
        coinbase_webhook.parse_event_data(event_data)

def test_map_status(coinbase_webhook: CoinbaseWebhook[ItemType]) -> None:
    assert coinbase_webhook._map_status('charge:created', '') == 'webhook_recieved'
    assert coinbase_webhook._map_status('charge:confirmed', 'completed') == 'paid'
    assert coinbase_webhook._map_status('charge:failed', '') == 'webhook_recieved'
    assert coinbase_webhook._map_status('charge:delayed', '') == 'sent_to_processor'
    assert coinbase_webhook._map_status('charge:pending', '') == 'sent_to_websocket'
    assert coinbase_webhook._map_status('unknown_event', '') == 'webhook_recieved'

def test_get_one_time_payment_data(coinbase_webhook: CoinbaseWebhook[ItemType]) -> None:
    event_data: CoinbaseWebhookData = {
        'transaction_id': 'tx123',
        'amount': 10.99,
        'currency': 'USD',
        'status': 'paid',
        'user_id': 'user123'
    }
    
    result = coinbase_webhook._get_one_time_payment_data(event_data)
    
    assert result['user_id'] == 'user123'
    assert result['item_category'] == ItemType.ONE_TIME_PAYMENT
    assert result['purchase_id'] == 'tx123'
    assert result['item_name'] == 'Coinbase Payment'
    assert result['status'] == 'paid'
    assert result['quantity'] == 1

@patch('builtins.print')
def test_process_event(mock_print: MagicMock, coinbase_webhook: CoinbaseWebhook[ItemType]) -> None:
    event_data = {
        'event': {
            'type': 'charge:confirmed',
            'data': {
                'code': 'tx123'
            }
        }
    }
    
    coinbase_webhook.process_event(event_data, False)
    
    mock_print.assert_called_with('Charge confirmed:', event_data) 