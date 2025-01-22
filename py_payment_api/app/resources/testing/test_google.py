import pytest
from typing import Any
from flask import Flask
from flask.testing import FlaskClient

def test_google_webhook_post_success(client: FlaskClient) -> None:
    """Test successful Google webhook POST request."""
    response = client.post('/webhook/google', json={
        'event': 'SUBSCRIPTION_PURCHASED',
        'resource': {
            'orderId': '1234567890',
            'packageName': 'com.example.app',
            'productId': 'premium_subscription',
            'purchaseToken': 'token123',
            'purchaseTime': 1234567890
        }
    })
    assert response.status_code == 200
    assert response.json == {'message': 'Google webhook received'}

def test_google_webhook_post_invalid_json(client: FlaskClient) -> None:
    """Test Google webhook POST request with invalid JSON."""
    response = client.post('/webhook/google', data='invalid json')
    assert response.status_code == 400
    assert response.json == {'error': 'Invalid JSON payload'}

def test_google_webhook_post_missing_event(client: FlaskClient) -> None:
    """Test Google webhook POST request with missing event."""
    response = client.post('/webhook/google', json={})
    assert response.status_code == 400
    assert response.json == {'error': 'Missing event in payload'}

def test_google_webhook_post_invalid_event(client: FlaskClient) -> None:
    """Test Google webhook POST request with invalid event type."""
    response = client.post('/webhook/google', json={'event': 'INVALID.EVENT'})
    assert response.status_code == 400
    assert response.json == {'error': 'Invalid event type'}

def test_google_webhook_post_missing_resource(client: FlaskClient) -> None:
    """Test Google webhook POST request with missing resource data."""
    response = client.post('/webhook/google', json={'event': 'SUBSCRIPTION_PURCHASED'})
    assert response.status_code == 400
    assert response.json == {'error': 'Missing resource data'} 