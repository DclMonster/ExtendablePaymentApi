import pytest
from flask import Flask
from app import configure_webhook, configure_creditor

@pytest.fixture
def app():
    app = Flask(__name__)
    configure_webhook(app)
    configure_creditor(app)
    return app

def test_combined_e2e(client):
    # Simulate a POST request to the webhook endpoint
    response = client.post('/webhook/paypal', json={'event': 'PAYMENT.SALE.COMPLETED'})
    assert response.status_code == 200
    assert response.json == {'status': 'success'}

    # Simulate a POST request to the creditor endpoint
    response = client.post('/creditor/transaction', json={'amount': 100, 'currency': 'USD'})
    assert response.status_code == 200
    assert response.json == {'status': 'success'} 