import pytest
from flask import Flask
from app import configure_creditor

@pytest.fixture
def app():
    app = Flask(__name__)
    configure_creditor(app)
    return app

def test_creditor_e2e(client):
    # Simulate a POST request to the creditor endpoint
    response = client.post('/creditor/transaction', json={'amount': 100, 'currency': 'USD'})
    assert response.status_code == 200
    assert response.json == {'status': 'success'} 