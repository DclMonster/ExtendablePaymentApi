import pytest
from ....testing.app import client
from ..mongo_controller import MongoController

# Example test case for MongoController
@pytest.fixture
def mongo_controller():
    return MongoController()

# Example test case for connecting to the database
def test_mongo_controller_connect(mongo_controller):
    mongo_controller.connect()
    assert mongo_controller.connection is not None 