import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_coinbase_webhook(client):
    response = client.post('/webhook/coinbase', json={'event': 'test'})
    assert response.status_code == 200
    assert response.json == {'status': 'success'} 