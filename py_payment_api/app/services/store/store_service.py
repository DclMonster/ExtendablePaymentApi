from typing import List, Dict, TypeVar, Generic, Optional, cast
from enum import StrEnum
from ..store.payment.abstract import ItemCollectionService
from .enum import AvailableItem, ItemType
from .payment import OneTimePaymentData, SubscriptionPaymentData, PurchaseDetail, PurchaseStatus
from typing import Any
ITEM_CATEGORY = TypeVar('ITEM_CATEGORY', bound=StrEnum)

class StoreServiceError(Exception):
    """Base exception for store service errors."""
    pass

class StoreService(Generic[ITEM_CATEGORY]):
    """Service for managing store items."""

    __item_collection_services: Dict[ItemType, ItemCollectionService[ITEM_CATEGORY]]

    def __init__(self, item_type_to_item_service : Dict[ItemType, ItemCollectionService[ITEM_CATEGORY]] | None = None) -> None:
        """Initialize the store service."""
        self.__item_collection_services = item_type_to_item_service or {}   

    def _get_service(self, item_type: ItemType) -> ItemCollectionService[ITEM_CATEGORY]:
        """Get the service for a specific item type."""
        service = self.__item_collection_services.get(item_type)
        if not service:
            raise StoreServiceError(f"No service available for item type: {item_type}")
        return service

    def get_item(self, item_type: ItemType, item_category: ITEM_CATEGORY, item_id: str) -> Optional[AvailableItem]:
        """Get a specific item."""
        service = self._get_service(item_type)
        result = service.get_item(item_category, item_id)
        return cast(Optional[AvailableItem], result)

    def get_all_items_by_type(self, item_type: ItemType) -> List[AvailableItem]:
        """Get all items of a specific type."""
        service = self._get_service(item_type)
        return cast(List[AvailableItem], service.get_all_items())
    
    def get_all_items(self) -> Dict[ItemType, List[AvailableItem]]:
        """Get all items grouped by type."""
        return {
            item_type: cast(List[AvailableItem], service.get_all_items())
            for item_type, service in self.__item_collection_services.items()
        }
    
    def get_orders_by_user_id(self, user_id: str) -> List[PurchaseDetail]:
        """Get all orders by user ID."""
        orders = []
        for service in self.__item_collection_services.values():
            orders.extend(service.get_orders_by_user_id(user_id))
        return orders

    def get_purchase_type(self, item_name: str) -> ItemType:
        """Get the purchase type of an item."""
        for service in self.__item_collection_services.values():
            if service.has_item(item_name):
                return service.item_type
        return ItemType.UNKNOWN
    
    def update_order_status(self, purchase_id: str, status: PurchaseStatus) -> None:
        """Update the status of an order."""
        updated = False
        for service in self.__item_collection_services.values():
            if service.has_order(purchase_id):
                service.change_order_status(purchase_id, status)
                updated = True
        if not updated:
            raise StoreServiceError(f"No order found with purchase ID: {purchase_id}")


