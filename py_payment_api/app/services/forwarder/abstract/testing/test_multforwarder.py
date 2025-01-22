import pytest
from typing import List, Dict, Any, TypeVar, cast
from enum import StrEnum
from ..multi_forwarder import MultiForwarder
from ..forwarder import Forwarder, PurchaseStatus

class TestEventType(StrEnum):
    PAYMENT_COMPLETED = "payment.completed"
    PAYMENT_FAILED = "payment.failed"

class MockForwarder(Forwarder):
    def __init__(self) -> None:
        super().__init__()
        self.forwarded_data: List[Dict[str, Any]] = []

    def forward_event(self, event_data: Dict[str, Any]) -> None:
        self.forwarded_data.append(event_data)

class TestMultiForwarder(MultiForwarder[TestEventType]):
    def __init__(self, forwarders: Dict[TestEventType, Forwarder]) -> None:
        super().__init__(forwarders)

    def _get_api_type(self, event_data: Dict[str, Any]) -> TestEventType:
        return TestEventType.PAYMENT_COMPLETED


@pytest.fixture
def multi_forwarder() -> MultiForwarder[TestEventType]:
    mock_forwarder = MockForwarder()
    forwarders: Dict[TestEventType, Forwarder] = {
        TestEventType.PAYMENT_COMPLETED: mock_forwarder
    }
    return TestMultiForwarder(forwarders=forwarders)

def test_multi_forwarder_add_forwarder() -> None:
    """Test creating a multi-forwarder with multiple forwarders."""
    forwarder1 = MockForwarder()
    forwarder2 = MockForwarder()
    forwarders: Dict[TestEventType, Forwarder] = {
        TestEventType.PAYMENT_COMPLETED: forwarder1,
        TestEventType.PAYMENT_FAILED: forwarder2
    }
    multi_forwarder = TestMultiForwarder(forwarders=forwarders)
    assert len(multi_forwarder.forwarders) == 2

def test_multi_forwarder_forward(multi_forwarder: MultiForwarder[TestEventType]) -> None:
    """Test forwarding data to multiple forwarders."""
    test_data: Dict[str, Any] = {"test": "data"}
    multi_forwarder.forward_event(test_data)

    forwarder = cast(MockForwarder, multi_forwarder.forwarders[TestEventType.PAYMENT_COMPLETED])
    assert len(forwarder.forwarded_data) == 1
    assert forwarder.forwarded_data[0] == test_data
