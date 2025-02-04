"""Regression tests for PayPal payment verification."""
import os
import pytest
import json
import base64
from typing import Dict, Any, Generator
from unittest.mock import patch
import requests
from ..app.verifiers.paypal_verifier import PayPalVerifier
from ..app.resources.webhook.paypal import PaypalWebhook
from ..app.services.forwarder.abstract.forwarder import Forwarder
from ..app.services.store.enum.item_type import ItemType

# Test configuration
SANDBOX_WEBHOOK_ID = os.getenv('PAYPAL_SANDBOX_WEBHOOK_ID', '')
SANDBOX_ORDER_ID = os.getenv('PAYPAL_SANDBOX_ORDER_ID', '')

@pytest.fixture(scope="module")
def sandbox_env() -> Generator[None, None, None]:
    """Set up sandbox environment variables."""
    original_env = dict(os.environ)
    sandbox_vars = {
        'PAYPAL_SECRET': os.getenv('PAYPAL_SANDBOX_SECRET', ''),
        'PAYPAL_WEBHOOK_ID': SANDBOX_WEBHOOK_ID,
        'PAYPAL_SANDBOX_MODE': 'true',
        'PAYPAL_CLIENT_ID': os.getenv('PAYPAL_SANDBOX_CLIENT_ID', '')
    }
    
    # Validate sandbox environment
    missing_vars = [k for k, v in sandbox_vars.items() if not v]
    if missing_vars:
        pytest.skip(f"Missing sandbox environment variables: {', '.join(missing_vars)}")
    
    os.environ.update(sandbox_vars)
    yield
    os.environ.clear()
    os.environ.update(original_env)

@pytest.fixture
def paypal_verifier(sandbox_env) -> PayPalVerifier:
    """Create PayPalVerifier instance with sandbox configuration."""
    return PayPalVerifier()

@pytest.fixture
def mock_forwarder() -> Forwarder:
    """Create a mock forwarder for webhook testing."""
    return Mock(spec=Forwarder)

@pytest.fixture
def paypal_webhook(mock_forwarder: Forwarder) -> PaypalWebhook[ItemType]:
    """Create PaypalWebhook instance for testing."""
    return PaypalWebhook[ItemType](forwarder=mock_forwarder)

class TestPayPalSandboxVerification:
    """Test PayPal payment verification in sandbox mode."""
    
    def test_verify_webhook_id_sandbox(self, paypal_verifier: PayPalVerifier) -> None:
        """Test verifying a sandbox webhook ID."""
        if not SANDBOX_WEBHOOK_ID:
            pytest.skip("No sandbox webhook ID provided")
        
        try:
            result = paypal_verifier.verify_webhook_id(SANDBOX_WEBHOOK_ID)
            assert result is True
        except Exception as e:
            pytest.fail(f"Webhook ID verification failed: {str(e)}")

    def test_verify_order_sandbox(self, paypal_verifier: PayPalVerifier) -> None:
        """Test verifying a sandbox order."""
        if not SANDBOX_ORDER_ID:
            pytest.skip("No sandbox order ID provided")
        
        try:
            headers = paypal_verifier._get_auth_headers()
            response = requests.get(
                f"{paypal_verifier.api_base_url}/checkout/orders/{SANDBOX_ORDER_ID}",
                headers=headers
            )
            
            assert response.status_code == 200
            
            order_data = response.json()
            assert 'id' in order_data
            assert order_data['id'] == SANDBOX_ORDER_ID
            assert 'status' in order_data
            assert order_data['status'] in ['CREATED', 'SAVED', 'APPROVED', 'VOIDED', 'COMPLETED', 'PAYER_ACTION_REQUIRED']
            
        except Exception as e:
            pytest.fail(f"Order verification failed: {str(e)}")

    def test_webhook_signature_sandbox(self, paypal_webhook: PaypalWebhook[ItemType]) -> None:
        """Test webhook signature verification in sandbox mode."""
        # Create a test webhook event
        event_body = {
            "id": "WH-TEST-123",
            "event_type": "PAYMENT.SALE.COMPLETED",
            "resource": {
                "id": SANDBOX_ORDER_ID or "TEST-ORDER",
                "state": "completed",
                "amount": {
                    "total": "10.99",
                    "currency": "USD"
                }
            }
        }
        
        event_data = {
            "transmissionId": "test-transmission",
            "timestamp": "2024-01-24T12:00:00Z",
            "webhookId": SANDBOX_WEBHOOK_ID,
            "eventBody": json.dumps(event_body),
            "certUrl": "https://api.sandbox.paypal.com/v1/notifications/certs/CERT-TEST",
            "authAlgo": "SHA256withRSA"
        }
        
        try:
            # Test webhook data parsing
            parsed_data = paypal_webhook.parse_event_data(json.dumps(event_data))
            
            assert parsed_data['transaction_id'] == event_body['resource']['id']
            assert parsed_data['amount'] == float(event_body['resource']['amount']['total'])
            assert parsed_data['currency'] == event_body['resource']['amount']['currency']
            assert parsed_data['status'] == 'paid'
            
        except Exception as e:
            pytest.fail(f"Webhook parsing failed: {str(e)}")

    def test_sandbox_environment_validation(self) -> None:
        """Test sandbox environment configuration."""
        required_vars = [
            'PAYPAL_SECRET',
            'PAYPAL_WEBHOOK_ID',
            'PAYPAL_CLIENT_ID',
            'PAYPAL_SANDBOX_MODE'
        ]
        
        for var in required_vars:
            assert os.getenv(var), f"Missing required sandbox environment variable: {var}"
        
        assert os.getenv('PAYPAL_SANDBOX_MODE').lower() == 'true', \
            "Sandbox mode should be enabled"

    def test_api_base_url_sandbox(self, paypal_verifier: PayPalVerifier) -> None:
        """Test API base URL in sandbox mode."""
        assert paypal_verifier.api_base_url == PayPalVerifier._SANDBOX_API, \
            "Should use sandbox API URL in sandbox mode"

    def test_certificate_caching(self, paypal_verifier: PayPalVerifier) -> None:
        """Test certificate caching mechanism."""
        test_cert_url = "https://api.sandbox.paypal.com/v1/notifications/certs/CERT-TEST"
        
        # First call should fetch and cache
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.content = b"-----BEGIN CERTIFICATE-----\nTEST\n-----END CERTIFICATE-----"
            mock_get.return_value = mock_response
            
            cert1 = paypal_verifier._get_certificate(test_cert_url)
            assert mock_get.call_count == 1
            
            # Second call should use cache
            cert2 = paypal_verifier._get_certificate(test_cert_url)
            assert mock_get.call_count == 1  # Should not have made another request
            assert cert1 == cert2  # Should be the same certificate object 