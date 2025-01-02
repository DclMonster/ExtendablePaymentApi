from .mongo import ItemCollectionService
from .items import AvailableItem
from typing import List, Dict, TypeVar, Generic
from enum import StrEnum
from .mongo import ItemType

ITEM_CATEGORY = TypeVar('ITEM_CATEGORY', bound=StrEnum)

class StoreService(Generic[ITEM_CATEGORY]):

    __item_collection_services : Dict[ItemType, ItemCollectionService[ITEM_CATEGORY]]
    def __init__(self, item_collection_services : List[ItemCollectionService[ITEM_CATEGORY]] = []):
        self.__item_collection_services = {item_collection_service.item_type: item_collection_service for item_collection_service in item_collection_services}

    def get_item(self, item_type: ItemType, item_category: ITEM_CATEGORY, item_id: str) -> AvailableItem:
        return self.__item_collection_services[item_type].get_item(item_category, item_id)

    def get_all_items(self, item_type: ItemType) -> List[AvailableItem]:
        return self.__item_collection_services[item_type].get_all_items()
