"""Test WooCommerce verifier."""
import os
import pytest
from unittest.mock import patch, MagicMock
import hmac
import hashlib
import json
from typing import Dict, Any

from ..woocommerce_verifier import WooCommerceVerifier, WooCommerceVerificationError

@pytest.fixture
def mock_env_vars():
    """Set up mock environment variables for testing."""
    with patch.dict('os.environ', {
        'WOOCOMMERCE_WEBHOOK_SECRET': 'test_webhook_secret',
        'WOOCOMMERCE_CONSUMER_KEY': 'test_consumer_key',
        'WOOCOMMERCE_CONSUMER_SECRET': 'test_consumer_secret',
        'WOOCOMMERCE_API_URL': 'https://test-store.com'
    }):
        yield

@pytest.fixture
def woocommerce_verifier(mock_env_vars) -> WooCommerceVerifier:
    """Create a WooCommerceVerifier instance for testing."""
    return WooCommerceVerifier()

@pytest.fixture
def mock_requests_get():
    """Mock requests.get function."""
    with patch('requests.get') as mock:
        yield mock

class TestWooCommerceVerifierInit:
    def test_init_success(self, mock_env_vars):
        """Test successful initialization."""
        verifier = WooCommerceVerifier()
        assert verifier._consumer_key == 'test_consumer_key'
        assert verifier._consumer_secret == 'test_consumer_secret'
        assert verifier._api_url == 'https://test-store.com'

    def test_init_missing_env_vars(self):
        """Test initialization with missing environment variables."""
        with pytest.raises(ValueError, match="Missing required WooCommerce configuration"):
            WooCommerceVerifier()

class TestWooCommerceVerifierSignature:
    def test_verify_signature_success(self, woocommerce_verifier: WooCommerceVerifier):
        """Test successful signature verification."""
        test_data = {'id': '1234', 'total': '99.99'}
        payload = str(test_data).encode('utf-8')
        
        # Create a valid signature
        computed = hmac.new(
            'test_webhook_secret'.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        result = woocommerce_verifier.verify_signature(test_data, computed)
        assert result is True

    def test_verify_signature_invalid(self, woocommerce_verifier: WooCommerceVerifier):
        """Test signature verification with invalid signature."""
        test_data = {'id': '1234', 'total': '99.99'}
        invalid_signature = 'invalid_signature'
        
        result = woocommerce_verifier.verify_signature(test_data, invalid_signature)
        assert result is False

    def test_verify_signature_error(self, woocommerce_verifier: WooCommerceVerifier):
        """Test signature verification with error."""
        test_data = None  # This will cause an error
        signature = 'any_signature'
        
        result = woocommerce_verifier.verify_signature(test_data, signature)
        assert result is False

class TestWooCommerceVerifierHeaders:
    def test_get_signature_from_header_success(self, woocommerce_verifier: WooCommerceVerifier):
        """Test successful signature extraction from headers."""
        headers = {'X-WC-Webhook-Signature': 'valid_signature'}
        signature = woocommerce_verifier.get_signature_from_header(headers)
        assert signature == 'valid_signature'

    def test_get_signature_from_header_missing(self, woocommerce_verifier: WooCommerceVerifier):
        """Test signature extraction with missing header."""
        headers = {}
        with pytest.raises(ValueError, match="Missing WooCommerce signature in headers"):
            woocommerce_verifier.get_signature_from_header(headers)

    def test_get_signature_from_header_invalid_type(self, woocommerce_verifier: WooCommerceVerifier):
        """Test signature extraction with invalid signature type."""
        headers = {'X-WC-Webhook-Signature': ['invalid', 'type']}
        with pytest.raises(ValueError, match="Invalid WooCommerce signature format"):
            woocommerce_verifier.get_signature_from_header(headers)

class TestWooCommerceVerifierOrder:
    def test_verify_order_success(self, woocommerce_verifier: WooCommerceVerifier, mock_requests_get):
        """Test successful order verification."""
        order_id = '1234'
        order_data = {
            'id': order_id,
            'total': '99.99',
            'status': 'completed'
        }
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = order_data
        mock_requests_get.return_value = mock_response
        
        result = woocommerce_verifier.verify_order(order_id)
        assert result['status'] == 'success'
        assert result['order'] == order_data
        
        mock_requests_get.assert_called_once_with(
            f'https://test-store.com/wp-json/wc/v3/orders/{order_id}',
            auth=('test_consumer_key', 'test_consumer_secret'),
            params={}
        )

    def test_verify_order_with_key(self, woocommerce_verifier: WooCommerceVerifier, mock_requests_get):
        """Test order verification with order key."""
        order_id = '1234'
        order_key = 'wc_order_abc123'
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'id': order_id}
        mock_requests_get.return_value = mock_response
        
        result = woocommerce_verifier.verify_order(order_id, order_key)
        assert result['status'] == 'success'
        
        mock_requests_get.assert_called_once_with(
            f'https://test-store.com/wp-json/wc/v3/orders/{order_id}',
            auth=('test_consumer_key', 'test_consumer_secret'),
            params={'order_key': order_key}
        )

    def test_verify_order_failure(self, woocommerce_verifier: WooCommerceVerifier, mock_requests_get):
        """Test order verification failure."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Order not found"
        mock_requests_get.return_value = mock_response
        
        result = woocommerce_verifier.verify_order('1234')
        assert result['status'] == 'error'
        assert 'Order not found' in result['error']['msg']

class TestWooCommerceVerifierSubscription:
    def test_verify_subscription_success(self, woocommerce_verifier: WooCommerceVerifier, mock_requests_get):
        """Test successful subscription verification."""
        subscription_id = '5678'
        subscription_data = {
            'id': subscription_id,
            'status': 'active'
        }
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = subscription_data
        mock_requests_get.return_value = mock_response
        
        result = woocommerce_verifier.verify_subscription(subscription_id)
        assert result['status'] == 'success'
        assert result['subscription'] == subscription_data

    def test_verify_subscription_failure(self, woocommerce_verifier: WooCommerceVerifier, mock_requests_get):
        """Test subscription verification failure."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Subscription not found"
        mock_requests_get.return_value = mock_response
        
        result = woocommerce_verifier.verify_subscription('5678')
        assert result['status'] == 'error'
        assert 'Subscription not found' in result['error']['msg']

class TestWooCommerceVerifierNotifications:
    @pytest.mark.parametrize("event,expected_type", [
        ('order.created', 'order_update'),
        ('order.updated', 'order_update'),
        ('subscription.created', 'subscription_update'),
        ('subscription.renewed', 'subscription_update'),
        ('subscription.cancelled', 'subscription_cancelled'),
        ('unknown.event', 'unknown_event')
    ])
    def test_handle_notification(self, woocommerce_verifier: WooCommerceVerifier, event, expected_type):
        """Test handling different notification types."""
        payload = {
            'webhook_event': event,
            'id': '1234',
            'status': 'completed',
            'line_items': [{'product_id': '789'}]
        }
        
        result = woocommerce_verifier.handle_notification(payload)
        assert result['type'] == expected_type
        
        if expected_type != 'unknown_event':
            assert result['status'] == 'action_update'
            assert 'update_body' in result
            assert 'identifier' in result

    def test_handle_notification_error(self, woocommerce_verifier: WooCommerceVerifier):
        """Test notification handling with error."""
        payload = None  # This will cause an error
        
        result = woocommerce_verifier.handle_notification(payload)
        assert result['status'] == 'error'
        assert result['type'] == 'processing_error'
        assert 'error' in result['update_body'] 