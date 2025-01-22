from typing import Dict, TypeVar, Generic, List, Tuple, Union, Any, Type
from ..enum import PaymentProvider, ItemType
from enum import StrEnum
from .abstract import BasePaymentData, PaymentHandler
from .abstract.item_collection_service import ItemCollectionService
from ..store_service import StoreService
from .subscription import SubscriptionPaymentHandler, SubscriptionPaymentData
from .one_time import OneTimePaymentHandler, OneTimePaymentData
from .provider_data import (
    AppleOneTimePaymentData,
    AppleSubscriptionPaymentData,
    PayPalOneTimePaymentData,
    GoogleOneTimePaymentData,
    CoinbaseOneTimePaymentData,
    CoinsnubOneTimePaymentData,
    PayPalSubscriptionPaymentData,
    GoogleSubscriptionPaymentData,
    CoinbaseSubscriptionPaymentData,
    CoinsnubSubscriptionPaymentData,
)

ONE_TIME_ITEM_CATEGORY = TypeVar("ONE_TIME_ITEM_CATEGORY", bound=StrEnum)
SUBSCRIPTION_ITEM_CATEGORY = TypeVar("SUBSCRIPTION_ITEM_CATEGORY", bound=StrEnum)
T = TypeVar('T', bound=BasePaymentData[Any])

class ServiceNotEnabledError(Exception):
    def __init__(self, message: str) -> None:
        self.__message = message

    def __str__(self) -> str:
        return self.__message

class PaymentService(Generic[ONE_TIME_ITEM_CATEGORY, SUBSCRIPTION_ITEM_CATEGORY]):
    """
    Service class for registering and executing actions based on different payment providers.
    """

    def __init__(self, enabled_providers: List[PaymentProvider]) -> None:
        self.__subscription_handlers: Dict[SUBSCRIPTION_ITEM_CATEGORY, SubscriptionPaymentHandler[SUBSCRIPTION_ITEM_CATEGORY, SubscriptionPaymentData[Any]]] = {}
        self.__one_time_handlers: Dict[ONE_TIME_ITEM_CATEGORY, OneTimePaymentHandler[ONE_TIME_ITEM_CATEGORY, OneTimePaymentData[Any]]] = {}
        self.__enabled_providers = enabled_providers


    def handle_subscription_payment(self, provider: PaymentProvider, category: SUBSCRIPTION_ITEM_CATEGORY, data: SubscriptionPaymentData[Any]) -> None:
        if provider not in self.__enabled_providers:
            raise ServiceNotEnabledError(f"{provider.value} service is not enabled.")
        self.__subscription_handlers[category].payment(data)

    def handle_one_time_payment(self, provider: PaymentProvider, category: ONE_TIME_ITEM_CATEGORY, data: OneTimePaymentData[Any]) -> None:
        if provider not in self.__enabled_providers:
            raise ServiceNotEnabledError(f"{provider.value} service is not enabled.")
        self.__one_time_handlers[category].payment(data)

    def register_subscription_handler(self, category: SUBSCRIPTION_ITEM_CATEGORY, handler: SubscriptionPaymentHandler[SUBSCRIPTION_ITEM_CATEGORY, SubscriptionPaymentData[Any]]) -> None:
        self.__subscription_handlers[category] = handler

    def register_one_time_handler(self, category: ONE_TIME_ITEM_CATEGORY, handler: OneTimePaymentHandler[ONE_TIME_ITEM_CATEGORY, OneTimePaymentData[Any]]) -> None:
        self.__one_time_handlers[category] = handler




