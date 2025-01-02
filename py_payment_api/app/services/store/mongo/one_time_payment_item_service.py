from .item_collection_service import ItemCollectionService
from .item_type import ItemType
from enum import StrEnum
from typing import TypeVar, Generic
ITEM_CATEGORY = TypeVar('ITEM_CATEGORY', bound=StrEnum)

class OneTimePaymentItemService(Generic[ITEM_CATEGORY], ItemCollectionService[ITEM_CATEGORY]):
    def __init__(self):
        super().__init__(ItemType.ONE_TIME_PAYMENT)
