import pytest
from unittest.mock import Mock, patch
import json
from datetime import datetime
from ..resources.webhook.woocommerce import WooCommerceWebhook, WooCommerceWebhookError
from ..services import PaymentProvider
from ..services.store.enum.item_type import ItemType
from ..verifiers.woocommerce_verifier import WooCommerceVerifier

@pytest.fixture
def mock_forwarder():
    forwarder = Mock()
    forwarder.forward = Mock(return_value=True)
    return forwarder

@pytest.fixture
def mock_verifier():
    with patch('app.verifiers.woocommerce_verifier.WooCommerceVerifier') as mock:
        verifier = mock.return_value
        verifier.verify_signature.return_value = True
        verifier.verify_order.return_value = {
            'status': 'success',
            'order': {
                'id': '12345',
                'line_items': [{
                    'name': 'Test Product',
                    'product_id': '789',
                    'quantity': 1
                }]
            }
        }
        yield verifier

@pytest.fixture
def webhook_handler(mock_forwarder, mock_verifier):
    return WooCommerceWebhook(forwarder=mock_forwarder)

@pytest.fixture
def valid_order_data():
    return {
        'id': '12345',
        'total': '99.99',
        'currency': 'USD',
        'status': 'completed',
        'customer_id': 'user123',
        'line_items': [{
            'product_id': '789',
            'name': 'Test Product',
            'type': 'simple'
        }],
        'order_key': 'wc_order_abc123',
        'payment_method': 'stripe',
        'payment_method_title': 'Credit Card',
        'customer_note': 'Test note',
        'created_via': 'checkout',
        'webhook_event': 'order.created'
    }

@pytest.fixture
def valid_subscription_data():
    return {
        'id': '12345',
        'total': '19.99',
        'currency': 'USD',
        'status': 'processing',
        'customer_id': 'user123',
        'line_items': [{
            'product_id': '999',
            'name': 'Premium Subscription',
            'type': 'subscription'
        }],
        'order_key': 'wc_order_xyz789',
        'payment_method': 'stripe',
        'payment_method_title': 'Credit Card',
        'webhook_event': 'subscription.created'
    }

class TestWooCommerceWebhook:
    def test_parse_valid_order(self, webhook_handler, valid_order_data):
        """Test parsing a valid order webhook."""
        result = webhook_handler.parse_event_data(json.dumps(valid_order_data))
        
        assert result['transaction_id'] == '12345'
        assert result['amount'] == 99.99
        assert result['currency'] == 'USD'
        assert result['status'] == 'paid'
        assert result['user_id'] == 'user123'
        assert result['is_subscription'] is False
        assert result['metadata']['order_key'] == 'wc_order_abc123'
        assert result['metadata']['webhook_event'] == 'order.created'

    def test_parse_valid_subscription(self, webhook_handler, valid_subscription_data):
        """Test parsing a valid subscription webhook."""
        result = webhook_handler.parse_event_data(json.dumps(valid_subscription_data))
        
        assert result['transaction_id'] == '12345'
        assert result['amount'] == 19.99
        assert result['currency'] == 'USD'
        assert result['status'] == 'sent_to_processor'
        assert result['is_subscription'] is True
        assert result['metadata']['webhook_event'] == 'subscription.created'

    def test_invalid_json(self, webhook_handler):
        """Test handling invalid JSON data."""
        with pytest.raises(WooCommerceWebhookError) as exc:
            webhook_handler.parse_event_data("invalid json")
        assert "Error parsing webhook data" in str(exc.value)

    def test_missing_required_fields(self, webhook_handler):
        """Test handling missing required fields."""
        invalid_data = {
            'status': 'completed',
            'currency': 'USD'
            # Missing 'id' and 'total'
        }
        with pytest.raises(WooCommerceWebhookError) as exc:
            webhook_handler.parse_event_data(json.dumps(invalid_data))
        assert "Missing required fields" in str(exc.value)

    def test_order_verification_failure(self, webhook_handler, valid_order_data, mock_verifier):
        """Test handling order verification failure."""
        mock_verifier.verify_order.side_effect = Exception("Verification failed")
        
        result = webhook_handler.parse_event_data(json.dumps(valid_order_data))
        assert 'verification_error' in result['metadata']
        assert "Verification failed" in result['metadata']['verification_error']

    def test_get_one_time_payment_data(self, webhook_handler, valid_order_data):
        """Test generating one-time payment data."""
        webhook_data = webhook_handler.parse_event_data(json.dumps(valid_order_data))
        payment_data = webhook_handler._get_one_time_payment_data(webhook_data)
        
        assert payment_data.user_id == 'user123'
        assert payment_data.item_category == ItemType.ONE_TIME_PAYMENT
        assert payment_data.purchase_id == '12345'
        assert "Product:" in payment_data.item_name
        assert payment_data.status == 'paid'
        assert payment_data.quantity == 1

    def test_get_subscription_payment_data(self, webhook_handler, valid_subscription_data):
        """Test generating subscription payment data."""
        webhook_data = webhook_handler.parse_event_data(json.dumps(valid_subscription_data))
        payment_data = webhook_handler._get_subscription_payment_data(webhook_data)
        
        assert payment_data.user_id == 'user123'
        assert payment_data.item_category == ItemType.SUBSCRIPTION
        assert payment_data.purchase_id == '12345'
        assert "Subscription:" in payment_data.item_name
        assert payment_data.status == 'sent_to_processor'

    def test_status_mapping(self, webhook_handler):
        """Test WooCommerce status mapping."""
        assert webhook_handler._map_status('completed') == 'paid'
        assert webhook_handler._map_status('processing') == 'sent_to_processor'
        assert webhook_handler._map_status('pending') == 'webhook_received'
        assert webhook_handler._map_status('unknown') == 'webhook_received'

    @pytest.mark.asyncio
    async def test_handle_webhook(self, webhook_handler, valid_order_data, mock_forwarder):
        """Test handling a complete webhook request."""
        event_data = json.dumps(valid_order_data)
        signature = "valid_signature"
        
        # Mock the request context
        with patch('flask.request') as mock_request:
            mock_request.get_data.return_value = event_data
            mock_request.headers = {'X-WC-Webhook-Signature': signature}
            
            await webhook_handler.handle_webhook()
            
            # Verify forwarder was called
            mock_forwarder.forward.assert_called_once()
            call_args = mock_forwarder.forward.call_args[0][0]
            assert call_args['transaction_id'] == '12345'
            assert call_args['status'] == 'paid' 