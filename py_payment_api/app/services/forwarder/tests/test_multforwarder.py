import pytest
from unittest.mock import Mock
from enum import StrEnum
from ..abstract.multiforwarder import MultiForwarder

class ApiType(StrEnum):
    API_ONE = "API_ONE"
    API_TWO = "API_TWO"

@pytest.fixture
def forwarders():
    forwarder_one = Mock()
    forwarder_two = Mock()
    return {
        ApiType.API_ONE: forwarder_one,
        ApiType.API_TWO: forwarder_two
    }

@pytest.fixture
def multi_forwarder(forwarders):
    return MultiForwarder(forwarders)

def test_forward_event(multi_forwarder, forwarders):
    event_data = {'api_type': ApiType.API_ONE, 'message': 'test'}
    multi_forwarder._on_forward_event(event_data)
    forwarders[ApiType.API_ONE].forward_event.assert_called_once_with(event_data)

def test_invalid_api_type(multi_forwarder):
    event_data = {'api_type': 'INVALID_API', 'message': 'test'}
    with pytest.raises(ValueError, match="Invalid or missing API type"):
        multi_forwarder._on_forward_event(event_data)
