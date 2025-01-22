from typing import Any
import pytest
from flask import Flask
from flask.testing import FlaskClient
from ..store import StoreItems
from .....testing.app import app

@pytest.fixture
def client() -> FlaskClient:
    return app.test_client()

@pytest.fixture
def resource() -> StoreItems:
    return StoreItems()

def test_store_resource_get(client: Any) -> None:
    # Act
    response = client.get('/store')
    
    # Assert
    assert response.status_code == 200
    assert response.json == {'message': 'Store resource accessed'}

def test_store_resource_post(client: Any) -> None:
    # Act
    response = client.post('/store')
    
    # Assert
    assert response.status_code == 405  # Method Not Allowed

def test_store_resource_put(client: Any) -> None:
    # Act
    response = client.put('/store')
    
    # Assert
    assert response.status_code == 405  # Method Not Allowed

def test_store_resource_delete(client: Any) -> None:
    # Act
    response = client.delete('/store')
    
    # Assert
    assert response.status_code == 405  # Method Not Allowed 