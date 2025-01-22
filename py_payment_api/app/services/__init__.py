from typing import TypeVar, Generic, List, Dict, Any, Union, cast
from enum import StrEnum
from .store.store_service import StoreService
from .store.enum import AvailableItem, PaymentProvider
from .store.payment.payment_service import PaymentService
from .store import construct_store_service
from .store.enum import ItemType
from .store.payment.abstract.base_payment_data import BasePaymentData
from .store.enum import ItemType
from .store.payment import (
    AppleOneTimePaymentData,
    AppleSubscriptionPaymentData,
    GoogleOneTimePaymentData,
    GoogleSubscriptionPaymentData,
    PayPalOneTimePaymentData,
    PayPalSubscriptionPaymentData,
    CoinbaseOneTimePaymentData,
    CoinbaseSubscriptionPaymentData,
    CoinsnubOneTimePaymentData,
    CoinsnubSubscriptionPaymentData,
    SubscriptionPaymentData,
    OneTimePaymentData,
    PurchaseDetail,
)
from .store.payment.one_time.one_time_payment_handler import OneTimePaymentHandler
from .store.payment.subscription.subscription_payment_handler import (
    SubscriptionPaymentHandler,
)
from .store.payment.abstract import ItemCollectionService
from .store.payment.abstract.item_collection_service import PurchaseStatus
import os
from .store.store_service import StoreServiceError
ONE_TIME_ITEM_CATEGORY = TypeVar("ONE_TIME_ITEM_CATEGORY", bound=StrEnum)
SUBSCRIPTION_ITEM_CATEGORY = TypeVar("SUBSCRIPTION_ITEM_CATEGORY", bound=StrEnum)
T = TypeVar("T", bound=BasePaymentData[Any])


class ServiceNotEnabledError(ValueError):
    """Raised when trying to use a service that is not enabled."""

    pass


class Services(Generic[ONE_TIME_ITEM_CATEGORY, SUBSCRIPTION_ITEM_CATEGORY]):
    __store_service: StoreService[
        Union[ONE_TIME_ITEM_CATEGORY, SUBSCRIPTION_ITEM_CATEGORY]
    ]
    __payment_service: PaymentService[
        ONE_TIME_ITEM_CATEGORY, SUBSCRIPTION_ITEM_CATEGORY
    ]
    __enabled_providers: List[PaymentProvider]

    def __init__(
        self,
        enabled_providers: List[PaymentProvider],
        item_type_to_item_service: Dict[
            ItemType,
            ItemCollectionService[
                Union[ONE_TIME_ITEM_CATEGORY, SUBSCRIPTION_ITEM_CATEGORY]
            ],
        ],
        sub_handlers: Dict[
            SUBSCRIPTION_ITEM_CATEGORY,
            SubscriptionPaymentHandler[
                SUBSCRIPTION_ITEM_CATEGORY, SubscriptionPaymentData[Any]
            ],
        ],
        one_time_handlers: Dict[
            ONE_TIME_ITEM_CATEGORY,
            OneTimePaymentHandler[ONE_TIME_ITEM_CATEGORY, OneTimePaymentData[Any]],
        ],
    ) -> None:
        self.__store_service = construct_store_service(item_type_to_item_service)
        self.__payment_service = PaymentService(enabled_providers)
        self.__enabled_providers = enabled_providers
        for handler in sub_handlers.values():
            self.__payment_service.register_subscription_handler(
                handler.category, handler
            )
        for one_time_handler in one_time_handlers.values():
            self.__payment_service.register_one_time_handler(
                one_time_handler.category, one_time_handler
            )

    def _check_service_enabled(self, provider: PaymentProvider) -> None:
        """Check if a service is enabled and raise an error if not."""
        if provider not in self.__enabled_providers:
            raise ServiceNotEnabledError(f"{provider.value} service is not enabled.")

    def get_orders_by_user_id(self, user_id: str) -> List[PurchaseDetail]:
        return self.__store_service.get_orders_by_user_id(user_id)

    def get_items(self, item_type: ItemType) -> List[AvailableItem]:
        return self.__store_service.get_all_items_by_type(item_type)

    def get_all_items(self) -> Dict[ItemType, List[AvailableItem]]:
        return self.__store_service.get_all_items()

    def get_purchase_type(self, item_name: str) -> ItemType:
        return self.__store_service.get_purchase_type(item_name)

    def _handle_one_time_payment(
        self, provider: PaymentProvider, payment_data: OneTimePaymentData[Any]
    ) -> None:
        """Generic payment handler."""
        self._check_service_enabled(provider)
        self.__payment_service.handle_one_time_payment(
            provider, payment_data["item_category"], payment_data
        )

    def _handle_subscription(
        self, provider: PaymentProvider, payment_data: SubscriptionPaymentData[Any]
    ) -> None:
        """Generic subscription handler."""
        self._check_service_enabled(provider)
        self.__payment_service.handle_subscription_payment(
            provider, payment_data["item_category"], payment_data
        )

    def change_order_status(self, order_id: str, purchase_status: PurchaseStatus) -> None:
        self.__store_service.update_order_status(order_id, purchase_status)

__services: Services[Any, Any] | None = None    

def init_services(
    enabled_providers: List[PaymentProvider],
    item_type_to_item_service: Dict[
        ItemType,
        ItemCollectionService[
            Union[ONE_TIME_ITEM_CATEGORY, SUBSCRIPTION_ITEM_CATEGORY]
        ],
    ],
    sub_handlers: Dict[
        SUBSCRIPTION_ITEM_CATEGORY,
        SubscriptionPaymentHandler[
            SUBSCRIPTION_ITEM_CATEGORY, SubscriptionPaymentData[Any]
        ],
    ],
    one_time_handlers: Dict[
        ONE_TIME_ITEM_CATEGORY,
        OneTimePaymentHandler[ONE_TIME_ITEM_CATEGORY, OneTimePaymentData[Any]],
    ],
) -> Services[ONE_TIME_ITEM_CATEGORY, SUBSCRIPTION_ITEM_CATEGORY]:
    global __services
    __services = Services(
        enabled_providers, item_type_to_item_service, sub_handlers, one_time_handlers
    )
    return __services

def get_services() -> Services[ONE_TIME_ITEM_CATEGORY, SUBSCRIPTION_ITEM_CATEGORY]:
    global __services
    if __services is None:
        raise ValueError("Services not initialized")
    return __services

__all__ = [
    "init_services",
    "Services",
    "PaymentProvider",
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
    "get_services",
    "StoreServiceError",
]
