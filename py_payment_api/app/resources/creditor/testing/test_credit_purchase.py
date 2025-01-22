import pytest
from flask import Flask, Response
from flask.testing import FlaskClient
from typing import cast, Dict, Any, TypedDict, NotRequired
from ..credit_purchase import CreditPurchase

class CreditPurchaseResponse(TypedDict):
    message: str
    transaction_id: NotRequired[str]

@pytest.fixture
def client(app: Flask) -> FlaskClient:
    return app.test_client()

@pytest.fixture
def app() -> Flask:
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.register_blueprint(CreditPurchase.blueprint)
    return app

# Example test case for a successful POST request
def test_credit_purchase_post(client: FlaskClient) -> None:
    response = client.post('/creditor/credit_purchase', json={'amount': 100, 'currency': 'USD'})
    json_data = cast(CreditPurchaseResponse, response.get_json())
    assert response.status_code == 200
    assert json_data['message'] == 'Credit purchase successful'
    assert 'transaction_id' in json_data
    assert isinstance(json_data['transaction_id'], str)

# Example test case for an invalid POST request
def test_credit_purchase_invalid_post(client: FlaskClient) -> None:
    # Test negative amount
    response = client.post('/creditor/credit_purchase', json={'amount': -100, 'currency': 'USD'})
    json_data = cast(CreditPurchaseResponse, response.get_json())
    assert response.status_code == 400
    assert json_data['message'] == 'Invalid amount'

    # Test missing amount
    response = client.post('/creditor/credit_purchase', json={'currency': 'USD'})
    json_data = cast(CreditPurchaseResponse, response.get_json())
    assert response.status_code == 400
    assert json_data['message'] == 'Amount is required'

    # Test invalid currency
    response = client.post('/creditor/credit_purchase', json={'amount': 100, 'currency': 'INVALID'})
    json_data = cast(CreditPurchaseResponse, response.get_json())
    assert response.status_code == 400
    assert json_data['message'] == 'Invalid currency'

    # Test missing currency
    response = client.post('/creditor/credit_purchase', json={'amount': 100})
    json_data = cast(CreditPurchaseResponse, response.get_json())
    assert response.status_code == 400
    assert json_data['message'] == 'Currency is required' 