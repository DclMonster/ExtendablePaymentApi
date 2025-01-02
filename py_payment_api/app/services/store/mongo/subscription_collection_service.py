from .item_collection_service import ItemCollectionService
from .item_type import ItemType
from typing import Generic, TypeVar
from enum import StrEnum
ITEM_CATEGORY = TypeVar('ITEM_CATEGORY', bound=StrEnum)
class SubscriptionCollectionService(Generic[ITEM_CATEGORY], ItemCollectionService[ITEM_CATEGORY]):
    def __init__(self):
        super().__init__(ItemType.SUBSCRIPTION)

