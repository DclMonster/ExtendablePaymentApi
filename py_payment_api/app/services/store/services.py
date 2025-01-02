from .store_service import StoreService
from .mongo import SubscriptionCollectionService, OneTimePaymentItemService
from enum import StrEnum
from typing import TypeVar

ITEM_CATEGORY = TypeVar('ITEM_CATEGORY', bound=StrEnum)


def construct_store_service() -> StoreService[ITEM_CATEGORY]:
    subscription_collection_service = SubscriptionCollectionService[ITEM_CATEGORY]()
    one_time_payment_item_service = OneTimePaymentItemService[ITEM_CATEGORY]()
    return StoreService([subscription_collection_service, one_time_payment_item_service])




__all__ = ['construct_store_service']