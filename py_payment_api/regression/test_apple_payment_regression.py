"""Regression tests for Apple payment verification."""
import os
import pytest
import base64
import json
from typing import Dict, Any, Generator
from unittest.mock import patch
import requests
from ..app.verifiers.apple_verifier import AppleVerifier
from ..app.resources.webhook.apple import AppleWebhook
from ..app.services.forwarder.abstract.forwarder import Forwarder
from ..app.services.store.enum.item_type import ItemType

# Test configuration
SANDBOX_RECEIPT = os.getenv('APPLE_TEST_RECEIPT', '')  # Get test receipt from env
SANDBOX_SUBSCRIPTION_ID = os.getenv('APPLE_TEST_SUBSCRIPTION_ID', '')

@pytest.fixture(scope="module")
def sandbox_env() -> Generator[None, None, None]:
    """Set up sandbox environment variables."""
    original_env = dict(os.environ)
    sandbox_vars = {
        'APPLE_PUBLIC_KEY': os.getenv('APPLE_SANDBOX_PUBLIC_KEY', ''),
        'APPLE_KEY_ID': os.getenv('APPLE_SANDBOX_KEY_ID', ''),
        'APPLE_ISSUER_ID': os.getenv('APPLE_SANDBOX_ISSUER_ID', ''),
        'APPLE_BUNDLE_ID': 'com.test.app.sandbox'
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
def apple_verifier(sandbox_env) -> AppleVerifier:
    """Create AppleVerifier instance with sandbox configuration."""
    return AppleVerifier()

@pytest.fixture
def mock_forwarder() -> Forwarder:
    """Create a mock forwarder for webhook testing."""
    return Mock(spec=Forwarder)

@pytest.fixture
def apple_webhook(mock_forwarder: Forwarder) -> AppleWebhook[ItemType]:
    """Create AppleWebhook instance for testing."""
    return AppleWebhook[ItemType](forwarder=mock_forwarder)

class TestAppleSandboxVerification:
    """Test Apple payment verification in sandbox mode."""
    
    def test_verify_receipt_sandbox(self, apple_verifier: AppleVerifier) -> None:
        """Test verifying a sandbox receipt."""
        if not SANDBOX_RECEIPT:
            pytest.skip("No sandbox receipt provided")
        
        try:
            result = apple_verifier.verify_receipt(SANDBOX_RECEIPT)
            
            # Verify response structure
            assert isinstance(result, dict)
            assert 'status' in result
            assert 'receipt' in result
            
            # Verify receipt status (0 = valid)
            assert result['status'] == 0
            
            # Verify receipt details
            receipt = result['receipt']
            assert 'bundle_id' in receipt
            assert receipt['bundle_id'] == os.environ['APPLE_BUNDLE_ID']
            
            # Verify in_app purchases if present
            if 'in_app' in receipt:
                for purchase in receipt['in_app']:
                    assert 'product_id' in purchase
                    assert 'transaction_id' in purchase
                    assert 'purchase_date' in purchase
        except ValueError as e:
            pytest.fail(f"Receipt verification failed: {str(e)}")

    def test_verify_subscription_sandbox(self, apple_verifier: AppleVerifier) -> None:
        """Test verifying a sandbox subscription."""
        if not SANDBOX_SUBSCRIPTION_ID:
            pytest.skip("No sandbox subscription ID provided")
        
        try:
            # Generate API token
            token = apple_verifier._generate_api_token()
            
            # Make request to subscription endpoint
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                f"{AppleVerifier._APPLE_STORE_CONNECT_API}/subscriptions/{SANDBOX_SUBSCRIPTION_ID}",
                headers=headers
            )
            
            assert response.status_code == 200
            
            data = response.json()
            assert 'data' in data
            subscription = data['data']
            
            # Verify subscription data
            assert subscription['type'] == 'subscriptions'
            assert subscription['id'] == SANDBOX_SUBSCRIPTION_ID
            assert 'attributes' in subscription
            
            # Verify subscription status
            attributes = subscription['attributes']
            assert 'status' in attributes
            assert attributes['status'] in ['ACTIVE', 'EXPIRED', 'IN_TRIAL']
            
        except Exception as e:
            pytest.fail(f"Subscription verification failed: {str(e)}")

    def test_webhook_signature_sandbox(self, apple_webhook: AppleWebhook[ItemType]) -> None:
        """Test webhook signature verification in sandbox mode."""
        # Create a test notification payload
        notification = {
            'notificationType': 'DID_RENEW',
            'subtype': 'RENEWAL',
            'notificationUUID': 'test-uuid',
            'data': {
                'bundleId': os.environ['APPLE_BUNDLE_ID'],
                'environment': 'Sandbox'
            }
        }
        
        try:
            # Sign the notification (in real sandbox this would come from Apple)
            token = apple_webhook._verifier._generate_api_token()
            
            # Test webhook processing
            headers = {'x-apple-signature': token}
            result = apple_webhook.verify_header_signature(notification, headers)
            
            assert result is True
            
        except Exception as e:
            pytest.fail(f"Webhook signature verification failed: {str(e)}")

    def test_sandbox_environment_validation(self) -> None:
        """Test sandbox environment configuration."""
        required_vars = [
            'APPLE_PUBLIC_KEY',
            'APPLE_KEY_ID',
            'APPLE_ISSUER_ID',
            'APPLE_BUNDLE_ID'
        ]
        
        for var in required_vars:
            assert os.getenv(var), f"Missing required sandbox environment variable: {var}"
        
        assert os.getenv('APPLE_BUNDLE_ID').endswith('.sandbox'), \
            "Sandbox bundle ID should end with .sandbox" 