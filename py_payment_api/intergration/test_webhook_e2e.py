import pytest
from flask import Flask
from app import configure_webhook

@pytest.fixture
def app():
    app = Flask(__name__)
    configure_webhook(app)
    return app

def test_webhook_e2e(client):
    # Simulate a POST request to the webhook endpoint
    response = client.post('/webhook/paypal', json={'event': 'PAYMENT.SALE.COMPLETED'})
    assert response.status_code == 200
    assert response.json == {'status': 'success'} 