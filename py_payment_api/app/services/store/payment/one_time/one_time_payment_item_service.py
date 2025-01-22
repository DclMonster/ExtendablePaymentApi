from ..abstract.item_collection_service import ItemCollectionService
from enum import StrEnum
from typing import TypeVar, Generic
from ....store.enum import ItemType
ITEM_CATEGORY = TypeVar('ITEM_CATEGORY', bound=StrEnum)

class OneTimePaymentItemService(Generic[ITEM_CATEGORY], ItemCollectionService[ITEM_CATEGORY]):
    def __init__(self) -> None:
        super().__init__(ItemType.ONE_TIME_PAYMENT, ItemType.ONE_TIME_PAYMENT)
