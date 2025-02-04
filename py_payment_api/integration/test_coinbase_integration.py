"""Integration tests for Coinbase payment verification."""
import os
import pytest
import json
from typing import Dict, Any, Generator
from ..app.verifiers.coinbase_verifier import CoinbaseVerifier
from ..app.resources.webhook.coinbase import CoinbaseWebhook
from ..app.services.forwarder.abstract.forwarder import Forwarder

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
def coinbase_webhook(mock_forwarder: Forwarder) -> CoinbaseWebhook:
    """Create a CoinbaseWebhook instance for testing."""
    return CoinbaseWebhook(forwarder=mock_forwarder)

@pytest.fixture
def test_charge_data() -> Dict[str, Any]:
    """Sample charge data for testing."""
    return {
        "name": "Test Product",
        "description": "Test product for integration testing",
        "pricing_type": "fixed_price",
        "local_price": {
            "amount": "10.00",
            "currency": "USD"
        },
        "metadata": {
            "user_id": "test_user_123",
            "product_id": "test_product_456"
        }
    }

@pytest.mark.integration
class TestCoinbaseIntegration:
    """Integration tests for Coinbase payment verification."""

    def test_create_and_verify_charge(self, coinbase_verifier: CoinbaseVerifier, test_charge_data: Dict[str, Any]) -> None:
        """Test creating and verifying a charge."""
        # Create a new charge
        charge = coinbase_verifier.create_charge(test_charge_data)
        assert charge is not None
        assert charge.get('id') is not None
        assert charge.get('code') is not None
        
        # Verify the created charge
        verified_charge = coinbase_verifier.verify_charge(charge['code'])
        assert verified_charge is not None
        assert verified_charge['code'] == charge['code']
        assert verified_charge['name'] == test_charge_data['name']
        assert verified_charge['pricing']['local']['amount'] == test_charge_data['local_price']['amount']

    def test_list_charges(self, coinbase_verifier: CoinbaseVerifier) -> None:
        """Test listing charges."""
        charges = coinbase_verifier.list_charges(limit=5)
        assert charges is not None
        assert 'data' in charges
        assert isinstance(charges['data'], list)
        assert len(charges['data']) <= 5

    def test_webhook_signature_verification(self, coinbase_verifier: CoinbaseVerifier) -> None:
        """Test webhook signature verification."""
        # Create test data
        test_data = {"event": {"type": "charge:confirmed", "data": {"code": "test_code"}}}
        test_json = json.dumps(test_data)
        
        # Create signature using the test secret
        signature = coinbase_verifier._create_test_signature(test_json)
        
        # Verify the signature
        assert coinbase_verifier.verify_signature(test_data, signature)

    def test_webhook_event_processing(self, coinbase_webhook: CoinbaseWebhook, test_charge_data: Dict[str, Any]) -> None:
        """Test webhook event processing."""
        # Create test event data
        event_data = {
            "event": {
                "type": "charge:confirmed",
                "data": {
                    "code": "test_code_123",
                    "pricing": {
                        "local": {
                            "amount": "10.00",
                            "currency": "USD"
                        }
                    },
                    "metadata": {
                        "user_id": "test_user_123"
                    },
                    "payments": [
                        {
                            "network": "ethereum",
                            "transaction_id": "0x123",
                            "status": "CONFIRMED",
                            "value": {
                                "local": {"amount": "10.00", "currency": "USD"},
                                "crypto": {"amount": "0.005", "currency": "ETH"}
                            }
                        }
                    ]
                }
            }
        }
        
        # Process the event
        webhook_data = coinbase_webhook.parse_event_data(json.dumps(event_data))
        assert webhook_data is not None
        assert webhook_data['transaction_id'] == "test_code_123"
        assert webhook_data['amount'] == 10.00
        assert webhook_data['currency'] == "USD"
        assert webhook_data['status'] == "paid"
        assert webhook_data['user_id'] == "test_user_123"
        assert webhook_data['payment_method'] == "ethereum" 