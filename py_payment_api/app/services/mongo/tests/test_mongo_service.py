import pytest
from ....testing.app import client
from ..mongo_service import MongoService

# Example test case for MongoService
@pytest.fixture
def mongo_service():
    return MongoService()

# Example test case for connecting to the database
def test_mongo_service_connect(mongo_service):
    # Assuming connect is a synchronous method for testing purposes
    mongo_service.connect()
    assert mongo_service.connection is not None

# Example test case for retrieving data
def test_mongo_service_get_data(mongo_service):
    data = mongo_service.get_data('collection')
    assert isinstance(data, list) 