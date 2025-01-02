from abc import ABC, abstractmethod
from typing import List, final, Generic, TypeVar, Literal 
from .item_type import ItemType
from ..items import AvailableItem
from enum import StrEnum
from ..mongo import MongoDBService
from pymongo.collection import Collection

ITEM_CATEGORY = TypeVar('ITEM_CATEGORY', bound=StrEnum)
class AvailableItemCollectionEntry(AvailableItem):
    item_type: str
    item_category: ITEM_CATEGORY

class ItemCollectionService(Generic[ITEM_CATEGORY], MongoDBService, ABC):

    __item_collection : Collection[AvailableItemCollectionEntry]
    __item_type : ItemType
    def __init__(self, item_type: ItemType):
        super().__init__('Store')
        self.__item_collection : Collection[AvailableItemCollectionEntry] = self._db[f'{item_type}_collections']
        self.__item_type = item_type

    @final
    def get_item(self, item_category: ITEM_CATEGORY, item_id: str) -> AvailableItem:
        return self.__item_collection.find_one({'item_category': item_category.value, 'item_id': item_id})
    
    @final
    def get_all_item_in_category(self, item_category: ITEM_CATEGORY) -> List[AvailableItemCollectionEntry]:
        return self.__item_collection.find({'item_category': item_category.value})

    @final
    def get_all_items(self) -> List[AvailableItemCollectionEntry]:
        return self.__item_collection.find()

    @property
    def item_type(self) -> ItemType:
        return self.__item_type

