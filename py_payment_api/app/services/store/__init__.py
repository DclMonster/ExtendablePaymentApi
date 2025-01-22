from .enum import PaymentProvider, AvailableItem
from .store_service import StoreService
from .payment.abstract import ItemCollectionService
from enum import StrEnum
from typing import TypeVar, Dict
from ..store.enum import ItemType
from .payment import SubscriptionPaymentHandler, OneTimePaymentHandler
from .payment.provider_data import (
    AppleOneTimePaymentData,
    AppleSubscriptionPaymentData,
    GoogleOneTimePaymentData,
    GoogleSubscriptionPaymentData,
    PayPalOneTimePaymentData,
    PayPalSubscriptionPaymentData,
    CoinbaseOneTimePaymentData,
    CoinbaseSubscriptionPaymentData,
    CoinsnubSubscriptionPaymentData,
    CoinsnubOneTimePaymentData,
)
from .store_service import StoreServiceError
ITEM_CATEGORY = TypeVar("ITEM_CATEGORY", bound=StrEnum)
def construct_store_service(
    item_type_to_item_service: Dict[ItemType, ItemCollectionService[ITEM_CATEGORY]]
) -> StoreService[ITEM_CATEGORY]:
    return StoreService(item_type_to_item_service)

__all__ = [
    "construct_store_service",
    "PaymentProvider",
    "AvailableItem",
    "StoreService",
    "ItemCollectionService",
    "ItemType",
    "AppleOneTimePaymentData",
    "AppleSubscriptionPaymentData",
    "GoogleOneTimePaymentData",
    "GoogleSubscriptionPaymentData",
    "PayPalOneTimePaymentData",
    "PayPalSubscriptionPaymentData",
    "CoinbaseOneTimePaymentData",
    "CoinbaseSubscriptionPaymentData",
    "CoinsnubOneTimePaymentData",
    "CoinsnubSubscriptionPaymentData",
    "SubscriptionPaymentHandler",
    "OneTimePaymentHandler",
    "StoreServiceError",
]
