import pytest
from typing import Any
from flask import Flask
from flask.testing import FlaskClient
import sys
from pathlib import Path

# Add the root directory to Python path for imports
root_dir = Path(__file__).parent.parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))

def test_paypal_webhook_post_success(client: FlaskClient) -> None:
    """Test successful PayPal webhook POST request."""
    response = client.post('/webhook/paypal', json={
        'event': 'PAYMENT.SALE.COMPLETED',
        'resource': {
            'id': '1234567890',
            'amount': {
                'total': '100.00',
                'currency': 'USD'
            }
        }
    })
    assert response.status_code == 200
    assert response.json == {'message': 'PayPal webhook received'}

def test_paypal_webhook_post_invalid_json(client: FlaskClient) -> None:
    """Test PayPal webhook POST request with invalid JSON."""
    response = client.post('/webhook/paypal', data='invalid json')
    assert response.status_code == 400
    assert response.json == {'error': 'Invalid JSON payload'}

def test_paypal_webhook_post_missing_event(client: FlaskClient) -> None:
    """Test PayPal webhook POST request with missing event."""
    response = client.post('/webhook/paypal', json={})
    assert response.status_code == 400
    assert response.json == {'error': 'Missing event in payload'}

def test_paypal_webhook_post_invalid_event(client: FlaskClient) -> None:
    """Test PayPal webhook POST request with invalid event type."""
    response = client.post('/webhook/paypal', json={'event': 'INVALID.EVENT'})
    assert response.status_code == 400
    assert response.json == {'error': 'Invalid event type'}

def test_paypal_webhook_post_missing_resource(client: FlaskClient) -> None:
    """Test PayPal webhook POST request with missing resource data."""
    response = client.post('/webhook/paypal', json={'event': 'PAYMENT.SALE.COMPLETED'})
    assert response.status_code == 400
    assert response.json == {'error': 'Missing resource data'} 