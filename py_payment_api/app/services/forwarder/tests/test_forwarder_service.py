import pytest
from ....testing.app import client
from ..forwarder_service import ForwarderService

# Example test case for ForwarderService
@pytest.fixture
def forwarder_service():
    return ForwarderService()

# Example test case for forwarding a message
def test_forwarder_service_forward_message(forwarder_service):
    result = forwarder_service.forward_message('message')
    assert result is True 