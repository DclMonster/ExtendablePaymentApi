import pytest
from flask import Flask
from .store import StoreResource
from ....testing.app import client


# Example test case
def test_store_resource_get(client):
    response = client.get('/store')
    assert response.status_code == 200
    assert response.json == {'message': 'Store resource accessed'} 