import pytest
from typing import Any
from flask import Flask
from flask.testing import FlaskClient

def test_apple_webhook_post_success(client: FlaskClient) -> None:
    """Test successful Apple webhook POST request."""
    response = client.post('/webhook/apple', json={
        'event': 'DID_RENEW',
        'resource': {
            'transactionId': '1234567890',
            'originalTransactionId': '0987654321',
            'webOrderLineItemId': 'order123',
            'bundleId': 'com.example.app',
            'productId': 'premium_subscription',
            'purchaseDate': '2023-01-01T00:00:00Z',
            'expiresDate': '2024-01-01T00:00:00Z'
        }
    })
    assert response.status_code == 200
    assert response.json == {'message': 'Apple webhook received'}

def test_apple_webhook_post_invalid_json(client: FlaskClient) -> None:
    """Test Apple webhook POST request with invalid JSON."""
    response = client.post('/webhook/apple', data='invalid json')
    assert response.status_code == 400
    assert response.json == {'error': 'Invalid JSON payload'}

def test_apple_webhook_post_missing_event(client: FlaskClient) -> None:
    """Test Apple webhook POST request with missing event."""
    response = client.post('/webhook/apple', json={})
    assert response.status_code == 400
    assert response.json == {'error': 'Missing event in payload'}

def test_apple_webhook_post_invalid_event(client: FlaskClient) -> None:
    """Test Apple webhook POST request with invalid event type."""
    response = client.post('/webhook/apple', json={'event': 'INVALID.EVENT'})
    assert response.status_code == 400
    assert response.json == {'error': 'Invalid event type'}

def test_apple_webhook_post_missing_resource(client: FlaskClient) -> None:
    """Test Apple webhook POST request with missing resource data."""
    response = client.post('/webhook/apple', json={'event': 'DID_RENEW'})
    assert response.status_code == 400
    assert response.json == {'error': 'Missing resource data'} 