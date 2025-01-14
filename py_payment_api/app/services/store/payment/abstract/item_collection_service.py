from abc import ABC, abstractmethod
from typing import List, final, Generic, TypeVar, Literal, TypedDict
from ...enum.item_type import ItemType
from pymongo.collection import Collection
from datetime import datetime
from enum import StrEnum
from ...enum import AvailableItem
from ....mongo import MongoDBService

ITEM_CATEGORY = TypeVar('ITEM_CATEGORY', bound=StrEnum)
class AvailableItemCollectionEntry(Generic[ITEM_CATEGORY], AvailableItem):
    item_type: str
    item_category: ITEM_CATEGORY

class PurchaseDetail(TypedDict):
    purchase_id:str
    item_id: str
    user_id: str
    time_bought : datetime

class PurchaceOrderStatus(PurchaseDetail):
    status: Literal["webhook_recieved"] | Literal["sent_to_websocket"]| Literal["sent_to_processor"]| Literal["paid"]


class ItemCollectionService(Generic[ITEM_CATEGORY], MongoDBService, ABC):

    __item_collection : Collection[AvailableItemCollectionEntry]
    __item_purchase_collection : Collection[PurchaceOrderStatus]
    __item_type : ItemType
    def __init__(self, item_type: ItemType):
        super().__init__('Store')
        self.__item_collection : Collection[AvailableItemCollectionEntry] = self._db[f'{item_type}_collections']
        self.__item_purchase_collection : Collection[PurchaceOrderStatus] = self._db[f'{item_type}_orders']
        self.__item_type = item_type

    @final
    def get_item(self, item_category: ITEM_CATEGORY, item_id: str) -> AvailableItem:
        item = self.__item_collection.find_one({'item_category': item_category.value, 'item_id': item_id})
        if item is None:
            raise ValueError(f"Item with id {item_id} not found in category {item_category}")
        return item
    
    @final
    def get_all_item_in_category(self, item_category: ITEM_CATEGORY) -> List[AvailableItemCollectionEntry]:
        return list(self.__item_collection.find({'item_category': item_category.value}))

    @final
    def get_all_items(self) -> List[AvailableItemCollectionEntry]:
        return list(self.__item_collection.find())


    def log_webhook_recieved(self, details: PurchaseDetail) -> None:
        self.__item_purchase_collection.insert_one({
            "status": "webhook_recieved",
            "item_id": details["item_id"],
            "user_id": details["user_id"],
            "time_bought": details["time_bought"],
            "purchase_id": details["purchase_id"]
        })
    
    def change_order_status(self,purchase_id : str, status : Literal["webhook_recieved"] | Literal["sent_to_websocket"]| Literal["sent_to_processor"]| Literal["paid"]) -> None:
        self.__item_purchase_collection.update_one({"purchase_id" : purchase_id}, {"$set" : {"status" : status}} )

    @property
    def item_type(self) -> ItemType:
        return self.__item_type
    
    


