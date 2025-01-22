import pytest
from typing import Dict, Any, Literal
from enum import StrEnum
from datetime import datetime
from ..item_collection_service import ItemCollectionService, PurchaseDetail, ItemType
from ......services import PurchaseStatus

class TestItemCategory(StrEnum):
    TEST_ITEM = "test_item"

class TestItemCollectionService(ItemCollectionService[TestItemCategory]):
    order_statuses: Dict[str, PurchaseStatus] = {}
    def __init__(self) -> None:
        super().__init__("test_collection", ItemType.ONE_TIME_PAYMENT)

    def change_order_status(self, purchase_id: str, status: PurchaseStatus) -> None:
        self.order_statuses[purchase_id] = status

    def get_purchase_details(self, purchase_id: str) -> PurchaseDetail:
        return {
            "user_id": "test123",
            "item_id": TestItemCategory.TEST_ITEM,
            "purchase_id": purchase_id,
            "time_bought": datetime.now(),
        }

@pytest.fixture
def item_collection_service() -> TestItemCollectionService:
    return TestItemCollectionService()

def test_item_collection_service_get_purchase_details(
    item_collection_service: TestItemCollectionService
) -> None:
    """Test getting purchase details."""
    details = item_collection_service.get_purchase_details("test123")
    assert details["purchase_id"] == "test123"
    assert details["item_id"] == TestItemCategory.TEST_ITEM

def test_item_collection_service_change_status(
    item_collection_service: TestItemCollectionService
) -> None:
    """Test changing order status."""
    item_collection_service.change_order_status("test123", PurchaseStatus.PAID) 
    assert item_collection_service.order_statuses["test123"] == PurchaseStatus.PAID