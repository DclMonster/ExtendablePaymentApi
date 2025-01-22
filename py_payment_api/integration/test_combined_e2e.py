import pytest
from typing import Dict, Any
from flask import Flask
from flask.testing import FlaskClient
from ..app.config import configure_creditor, configure_webhook
from ..app.services.forwarder.restful_forwarder import RestfulForwarder
from ..app.services.store.enum.payment_provider import PaymentProvider

@pytest.fixture
def app() -> Flask:
    """Create a test Flask application."""
    app = Flask(__name__)
    enabled_providers = [
        PaymentProvider.PAYPAL,
        PaymentProvider.GOOGLE,
        PaymentProvider.COINBASE,
        PaymentProvider.APPLE,
        PaymentProvider.COINSUB
    ]
    forwarder = RestfulForwarder(url="http://test-endpoint.com")
    configure_webhook(app, enabled_providers, forwarder)
    configure_creditor(app)
    return app

@pytest.fixture
def client(app: Flask) -> FlaskClient:
    """Create a test client."""
    return app.test_client()

def test_combined_e2e(client: FlaskClient) -> None:
    """Test combined webhook and creditor endpoints end-to-end."""
    # Test webhook endpoint
    webhook_data: Dict[str, Any] = {
        'event': 'PAYMENT.SALE.COMPLETED',
        'data': {
            'payment_id': 'test123',
            'amount': 100,
            'currency': 'USD',
            'status': 'completed'
        }
    }
    response = client.post('/webhook/paypal', json=webhook_data)
    assert response.status_code == 200
    assert response.json == {'status': 'success'}

    # Test creditor endpoint
    creditor_data: Dict[str, Any] = {
        'amount': 100,
        'currency': 'USD',
        'user_id': 'test123',
        'item_name': 'test_item',
        'purchase_id': 'purchase123',
        'time_bought': '2024-01-19T00:00:00Z',
        'status': 'pending'
    }
    response = client.post('/creditor/transaction', json=creditor_data)
    assert response.status_code == 200
    assert response.json == {'status': 'success'} 