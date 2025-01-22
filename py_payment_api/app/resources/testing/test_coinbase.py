import pytest
from typing import Any
from flask import Flask
from flask.testing import FlaskClient

def test_coinbase_webhook_post_success(client: FlaskClient) -> None:
    """Test successful Coinbase webhook POST request."""
    response = client.post('/webhook/coinbase', json={
        'event': 'charge:confirmed',
        'data': {
            'id': '1234567890',
            'code': 'CHARGE123',
            'name': 'Premium Subscription',
            'pricing_type': 'fixed_price',
            'metadata': {
                'customer_id': 'user123',
                'product_id': 'premium_sub'
            },
            'payments': [
                {
                    'network': 'ethereum',
                    'transaction_id': 'tx123',
                    'status': 'CONFIRMED',
                    'value': {
                        'local': {'amount': '100.00', 'currency': 'USD'},
                        'crypto': {'amount': '0.05', 'currency': 'ETH'}
                    }
                }
            ]
        }
    })
    assert response.status_code == 200
    assert response.json == {'message': 'Coinbase webhook received'}

def test_coinbase_webhook_post_invalid_json(client: FlaskClient) -> None:
    """Test Coinbase webhook POST request with invalid JSON."""
    response = client.post('/webhook/coinbase', data='invalid json')
    assert response.status_code == 400
    assert response.json == {'error': 'Invalid JSON payload'}

def test_coinbase_webhook_post_missing_event(client: FlaskClient) -> None:
    """Test Coinbase webhook POST request with missing event."""
    response = client.post('/webhook/coinbase', json={})
    assert response.status_code == 400
    assert response.json == {'error': 'Missing event in payload'}

def test_coinbase_webhook_post_invalid_event(client: FlaskClient) -> None:
    """Test Coinbase webhook POST request with invalid event type."""
    response = client.post('/webhook/coinbase', json={'event': 'INVALID.EVENT'})
    assert response.status_code == 400
    assert response.json == {'error': 'Invalid event type'}

def test_coinbase_webhook_post_missing_data(client: FlaskClient) -> None:
    """Test Coinbase webhook POST request with missing data."""
    response = client.post('/webhook/coinbase', json={'event': 'charge:confirmed'})
    assert response.status_code == 400
    assert response.json == {'error': 'Missing data in payload'} 