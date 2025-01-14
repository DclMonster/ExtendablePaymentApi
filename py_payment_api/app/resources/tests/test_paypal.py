import pytest
from flask import Flask
from ....testing.app import client

# Example test case for a successful POST request
def test_paypal_webhook_post(client):
    response = client.post('/webhook/paypal', json={'event': 'test_event'})
    assert response.status_code == 200
    assert response.json == {'message': 'PayPal webhook received'} 