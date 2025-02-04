"""Regression tests for Coinbase payment verification."""
import os
import pytest
import json
import time
from typing import Dict, Any, Generator
from ..app.verifiers.coinbase_verifier import CoinbaseVerifier
from ..app.resources.webhook.coinbase import CoinbaseWebhook
from ..app.services.forwarder.abstract.forwarder import Forwarder
from ..app.services.store.enum.item_type import ItemType

# Skip tests if required environment variables are not set
pytestmark = pytest.mark.skipif(
    not all([
        os.getenv('COINBASE_API_KEY'),
        os.getenv('COINBASE_SECRET'),
        os.getenv('COINBASE_TEST_CHARGE_CODE'),
        os.getenv('COINBASE_TEST_WEBHOOK_SECRET')
    ]),
    reason="Missing required environment variables for Coinbase regression tests"
)

@pytest.fixture
def coinbase_verifier() -> CoinbaseVerifier:
    """Create a CoinbaseVerifier instance for testing."""
    return CoinbaseVerifier()

@pytest.fixture
def mock_forwarder() -> Forwarder:
    """Create a mock forwarder for testing."""
    class MockForwarder(Forwarder):
        def forward_event(self, event_data: Dict[str, Any]) -> None:
            print(f"Forwarding event: {event_data}")
    return MockForwarder()

@pytest.fixture
def coinbase_webhook(mock_forwarder: Forwarder) -> CoinbaseWebhook[ItemType]:
    """Create a CoinbaseWebhook instance for testing."""
    return CoinbaseWebhook[ItemType](forwarder=mock_forwarder)

@pytest.fixture
def test_charge_data() -> Dict[str, Any]:
    """Sample charge data for testing."""
    return {
        "name": "Regression Test Product",
        "description": "Product for regression testing",
        "pricing_type": "fixed_price",
        "local_price": {
            "amount": "5.00",
            "currency": "USD"
        },
        "metadata": {
            "user_id": "regression_test_user",
            "product_id": "regression_test_product"
        }
    }

@pytest.mark.regression
class TestCoinbaseRegression:
    """Regression tests for Coinbase payment verification."""

    def test_sandbox_charge_creation(self, coinbase_verifier: CoinbaseVerifier, test_charge_data: Dict[str, Any]) -> None:
        """Test creating a charge in sandbox mode."""
        # Ensure sandbox mode is enabled
        assert os.getenv('COINBASE_SANDBOX_MODE') == 'true', "Sandbox mode must be enabled for regression tests"
        
        # Create a new charge
        charge = coinbase_verifier.create_charge(test_charge_data)
        assert charge is not None
        assert charge.get('id') is not None
        assert charge.get('code') is not None
        assert charge['pricing']['local']['amount'] == test_charge_data['local_price']['amount']
        assert charge['metadata']['user_id'] == test_charge_data['metadata']['user_id']

    def test_sandbox_charge_verification(self, coinbase_verifier: CoinbaseVerifier) -> None:
        """Test verifying a charge in sandbox mode."""
        # Get test charge code from environment
        test_charge_code = os.getenv('COINBASE_TEST_CHARGE_CODE')
        assert test_charge_code is not None
        
        # Verify the test charge
        charge = coinbase_verifier.verify_charge(test_charge_code)
        assert charge is not None
        assert charge['code'] == test_charge_code
        assert charge['timeline'][-1]['status'] in ['NEW', 'PENDING', 'COMPLETED', 'EXPIRED']

    def test_sandbox_webhook_processing(self, coinbase_webhook: CoinbaseWebhook[ItemType], test_charge_data: Dict[str, Any]) -> None:
        """Test processing webhook events in sandbox mode."""
        # Create a test charge
        verifier = CoinbaseVerifier()
        charge = verifier.create_charge(test_charge_data)
        
        # Create test webhook event
        event_data = {
            "event": {
                "type": "charge:confirmed",
                "data": {
                    "code": charge['code'],
                    "pricing": charge['pricing'],
                    "metadata": charge['metadata'],
                    "payments": [
                        {
                            "network": "ethereum",
                            "transaction_id": "0xtest123",
                            "status": "CONFIRMED",
                            "value": {
                                "local": charge['pricing']['local'],
                                "crypto": {"amount": "0.003", "currency": "ETH"}
                            }
                        }
                    ]
                }
            }
        }
        
        # Process the webhook event
        webhook_data = coinbase_webhook.parse_event_data(json.dumps(event_data))
        assert webhook_data is not None
        assert webhook_data['transaction_id'] == charge['code']
        assert float(webhook_data['amount']) == float(test_charge_data['local_price']['amount'])
        assert webhook_data['status'] == "paid"
        assert webhook_data['user_id'] == test_charge_data['metadata']['user_id']

    def test_sandbox_charge_lifecycle(self, coinbase_verifier: CoinbaseVerifier, test_charge_data: Dict[str, Any]) -> None:
        """Test the complete lifecycle of a charge in sandbox mode."""
        # Create a charge
        charge = coinbase_verifier.create_charge(test_charge_data)
        assert charge['status'] == "NEW"
        
        # Store the charge code
        charge_code = charge['code']
        
        # Wait briefly to allow for status updates
        time.sleep(2)
        
        # Verify the charge status
        updated_charge = coinbase_verifier.verify_charge(charge_code)
        assert updated_charge['status'] in ['NEW', 'PENDING', 'EXPIRED']
        
        # List charges and verify the test charge is included
        charges = coinbase_verifier.list_charges(limit=10)
        charge_codes = [c['code'] for c in charges['data']]
        assert charge_code in charge_codes

    def test_sandbox_webhook_signature(self, coinbase_verifier: CoinbaseVerifier, test_charge_data: Dict[str, Any]) -> None:
        """Test webhook signature verification in sandbox mode."""
        # Create test webhook data
        webhook_data = {
            "event": {
                "type": "charge:created",
                "data": test_charge_data
            }
        }
        
        # Get webhook secret from environment
        webhook_secret = os.getenv('COINBASE_TEST_WEBHOOK_SECRET')
        assert webhook_secret is not None
        
        # Create signature
        json_data = json.dumps(webhook_data)
        signature = coinbase_verifier._create_test_signature(json_data)
        
        # Verify signature
        assert coinbase_verifier.verify_signature(webhook_data, signature) 