from .enum import PaymentProvider, AvailableItem
from .store_service import StoreService
from ..store.payment.subscription_collection_service import SubscriptionCollectionService
from ..store.payment.one_time_payment_item_service import OneTimePaymentItemService
from enum import StrEnum
from typing import TypeVar, Generic

ITEM_CATEGORY = TypeVar('ITEM_CATEGORY', bound=StrEnum)

def construct_store_service() -> StoreService[ITEM_CATEGORY]:
    subscription_collection_service : SubscriptionCollectionService[ITEM_CATEGORY] = SubscriptionCollectionService()
    one_time_payment_item_service : OneTimePaymentItemService[ITEM_CATEGORY] = OneTimePaymentItemService()
    return StoreService([subscription_collection_service, one_time_payment_item_service])

__all__ = ['construct_store_service', 'PaymentProvider', 'AvailableItem', 'StoreService']