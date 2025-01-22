from ..abstract.item_collection_service import ItemCollectionService
from ....store.enum import ItemType

from typing import Generic, TypeVar
from enum import StrEnum
ITEM_CATEGORY = TypeVar('ITEM_CATEGORY', bound=StrEnum)
class SubscriptionCollectionService(Generic[ITEM_CATEGORY], ItemCollectionService[ITEM_CATEGORY]):
    def __init__(self) -> None:
        super().__init__(ItemType.SUBSCRIPTION, ItemType.SUBSCRIPTION)

