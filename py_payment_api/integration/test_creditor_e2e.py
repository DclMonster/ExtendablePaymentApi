import pytest
from typing import Dict, Any
from flask import Flask
from flask.testing import FlaskClient
from ..app.config import configure_creditor

@pytest.fixture
def app() -> Flask:
    """Create a test Flask application."""
    app = Flask(__name__)
    configure_creditor(app)
    return app

@pytest.fixture
def client(app: Flask) -> FlaskClient:
    """Create a test client."""
    return app.test_client()

def test_creditor_e2e(client: FlaskClient) -> None:
    """Test creditor endpoint end-to-end."""
    test_data: Dict[str, Any] = {
        'amount': 100,
        'currency': 'USD',
        'user_id': 'test123',
        'item_name': 'test_item',
        'purchase_id': 'purchase123',
        'time_bought': '2024-01-19T00:00:00Z',
        'status': 'pending'
    }
    response = client.post('/creditor/transaction', json=test_data)
    assert response.status_code == 200
    assert response.json == {'status': 'success'} 