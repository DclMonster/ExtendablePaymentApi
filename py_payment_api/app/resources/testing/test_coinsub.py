import pytest
from typing import Any
from flask import Flask
from flask.testing import FlaskClient

def test_coinsub_webhook_post_success(client: FlaskClient) -> None:
    """Test successful CoinSub webhook POST request."""
    response = client.post('/webhook/coinsub', json={
        'event': 'payment.completed',
        'data': {
            'payment_id': '1234567890',
            'subscription_id': 'sub123',
            'customer_id': 'user123',
            'amount': '100.00',
            'currency': 'USD',
            'status': 'completed',
            'payment_method': {
                'type': 'crypto',
                'currency': 'BTC',
                'amount': '0.003'
            }
        }
    })
    assert response.status_code == 200
    assert response.json == {'message': 'CoinSub webhook received'}

def test_coinsub_webhook_post_invalid_json(client: FlaskClient) -> None:
    """Test CoinSub webhook POST request with invalid JSON."""
    response = client.post('/webhook/coinsub', data='invalid json')
    assert response.status_code == 400
    assert response.json == {'error': 'Invalid JSON payload'}

def test_coinsub_webhook_post_missing_event(client: FlaskClient) -> None:
    """Test CoinSub webhook POST request with missing event."""
    response = client.post('/webhook/coinsub', json={})
    assert response.status_code == 400
    assert response.json == {'error': 'Missing event in payload'}

def test_coinsub_webhook_post_invalid_event(client: FlaskClient) -> None:
    """Test CoinSub webhook POST request with invalid event type."""
    response = client.post('/webhook/coinsub', json={'event': 'INVALID.EVENT'})
    assert response.status_code == 400
    assert response.json == {'error': 'Invalid event type'}

def test_coinsub_webhook_post_missing_data(client: FlaskClient) -> None:
    """Test CoinSub webhook POST request with missing data."""
    response = client.post('/webhook/coinsub', json={'event': 'payment.completed'})
    assert response.status_code == 400
    assert response.json == {'error': 'Missing data in payload'} 