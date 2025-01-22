import pytest
from flask import Flask
from flask.testing import FlaskClient
from ..app.config import configure_webhook
from ..app.services.store.enum.payment_provider import PaymentProvider
from ..app.services.forwarder.restful_forwarder import RestfulForwarder

@pytest.fixture
def app() -> Flask:
    app = Flask(__name__)
    enabled_providers = [PaymentProvider.PAYPAL]
    forwarder = RestfulForwarder(url="http://test-endpoint.com")
    configure_webhook(app, enabled_providers, forwarder)
    return app

@pytest.fixture
def client(app: Flask) -> FlaskClient:
    return app.test_client()

def test_webhook_e2e(client: FlaskClient) -> None:
    # Simulate a POST request to the webhook endpoint
    response = client.post('/webhook/paypal', json={'event': 'PAYMENT.SALE.COMPLETED'})
    assert response.status_code == 200
    assert response.json == {'status': 'success'} 