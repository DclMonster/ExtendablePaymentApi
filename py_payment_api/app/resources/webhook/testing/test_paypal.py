import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from ....services import PaymentProvider
from ....services.store.enum.item_type import ItemType
from ..paypal import PaypalWebhook, PaypalWebhookError, PaypalWebhookData
from ....services.forwarder.abstract.forwarder import Forwarder, ForwarderType
from ....services.store.payment.one_time.one_time_payment_data import OneTimePaymentData
from ....services.store.payment.subscription.subscription_payment_data import SubscriptionPaymentData
from typing import Dict, Any, TypedDict, cast, Literal
import math

@pytest.fixture
def mock_forwarder() -> Forwarder:
    return Mock(spec=Forwarder)

@pytest.fixture
def paypal_webhook(mock_forwarder: Forwarder) -> PaypalWebhook[ItemType]:
    return PaypalWebhook[ItemType](forwarder=mock_forwarder)

def test_parse_event_data_success(paypal_webhook: PaypalWebhook[ItemType]) -> None:
    event_data = '''
    {
        "event_type": "PAYMENT.SALE.COMPLETED",
        "resource": {
            "id": "tx123",
            "amount": {
                "total": "10.99",
                "currency": "USD"
            },
            "custom_id": "user123",
            "state": "completed",
            "billing_agreement_id": "sub123"
        }
    }
    '''
    
    result = paypal_webhook.parse_event_data(event_data)
    
    assert result['transaction_id'] == 'tx123'
    assert isinstance(result['amount'], float)
    assert math.isclose(result['amount'], 10.99, rel_tol=1e-9)
    assert result['currency'] == 'USD'
    assert result['status'] == 'paid'
    assert result['user_id'] == 'user123'
    assert result['subscription_id'] == 'sub123'

def test_parse_event_data_missing_fields(paypal_webhook: PaypalWebhook[ItemType]) -> None:
    event_data = '''
    {
        "event_type": "PAYMENT.SALE.COMPLETED",
        "resource": {
            "amount": {
                "total": "10.99",
                "currency": "USD"
            }
        }
    }
    '''
    
    with pytest.raises(PaypalWebhookError, match="Missing required fields: transaction_id, status"):
        paypal_webhook.parse_event_data(event_data)

def test_parse_event_data_invalid_json(paypal_webhook: PaypalWebhook[ItemType]) -> None:
    event_data = 'invalid json'
    
    with pytest.raises(PaypalWebhookError, match="Error parsing event data"):
        paypal_webhook.parse_event_data(event_data)

def test_map_status(paypal_webhook: PaypalWebhook[ItemType]) -> None:
    assert paypal_webhook._map_status('PAYMENT.SALE.COMPLETED', 'completed') == 'paid'
    assert paypal_webhook._map_status('PAYMENT.SALE.PENDING', 'pending') == 'sent_to_websocket'
    assert paypal_webhook._map_status('PAYMENT.SALE.DENIED', 'denied') == 'webhook_recieved'
    assert paypal_webhook._map_status('BILLING.SUBSCRIPTION.CREATED', 'active') == 'webhook_recieved'
    assert paypal_webhook._map_status('BILLING.SUBSCRIPTION.CANCELLED', 'cancelled') == 'sent_to_processor'
    assert paypal_webhook._map_status('unknown_event', '') == 'webhook_recieved'

def test_get_one_time_payment_data(paypal_webhook: PaypalWebhook[ItemType]) -> None:
    event_data: PaypalWebhookData = {
        'transaction_id': 'tx123',
        'amount': 10.99,
        'currency': 'USD',
        'status': 'paid',
        'user_id': 'user123',
        'subscription_id': 'sub123'
    }
    
    result = paypal_webhook._get_one_time_payment_data(event_data)
    
    assert result['user_id'] == 'user123'
    assert result['item_category'] == ItemType.ONE_TIME_PAYMENT
    assert result['purchase_id'] == 'tx123'
    assert result['item_name'] == 'PayPal Payment'
    assert result['status'] == 'paid'
    assert result['quantity'] == 1

def test_get_subscription_payment_data(paypal_webhook: PaypalWebhook[ItemType]) -> None:
    event_data: PaypalWebhookData = {
        'transaction_id': 'tx123',
        'amount': 10.99,
        'currency': 'USD',
        'status': 'paid',
        'user_id': 'user123',
        'subscription_id': 'sub123'
    }
    
    result = paypal_webhook._get_subscription_payment_data(event_data)
    
    assert result['user_id'] == 'user123'
    assert result['item_category'] == ItemType.SUBSCRIPTION
    assert result['purchase_id'] == 'tx123'
    assert result['item_name'] == 'sub123'
    assert result['status'] == 'paid'

@patch('builtins.print')
def test_process_event(mock_print: MagicMock, paypal_webhook: PaypalWebhook[ItemType]) -> None:
    event_data = {
        'event_type': 'PAYMENT.SALE.COMPLETED',
        'resource': {
            'id': 'tx123',
            'state': 'completed'
        }
    }
    
    paypal_webhook.process_event(event_data, False)
    
    mock_print.assert_called_with('Payment completed:', event_data) 