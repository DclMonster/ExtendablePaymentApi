from .config import configure_creditor, configure_webhook
from flask import Flask
from typing import List, Dict, Any, TypeVar, Union

from .services.store.payment import PaymentHandler, BasePaymentData, SubscriptionPaymentHandler, OneTimePaymentHandler
from .services.store.payment.abstract import ItemCollectionService
from .services.store.payment.abstract.item_collection_service import ItemType
from .services.store.enum import PaymentProvider
from enum import StrEnum
from .services import init_services
from .services.store import SubscriptionPaymentHandler, OneTimePaymentHandler
from .services import SubscriptionPaymentData, OneTimePaymentData
from .services.forwarder.abstract.forwarder import Forwarder
ONE_TIME_ITEM_CATEGORY = TypeVar('ONE_TIME_ITEM_CATEGORY', bound=StrEnum)
SUBSCRIPTION_ITEM_CATEGORY = TypeVar('SUBSCRIPTION_ITEM_CATEGORY', bound=StrEnum)

def creditor_configure(
    app: Flask,
    item_type_to_item_service: Dict[ItemType, ItemCollectionService[Union[ONE_TIME_ITEM_CATEGORY, SUBSCRIPTION_ITEM_CATEGORY]]],
    sub_handlers: Dict[SUBSCRIPTION_ITEM_CATEGORY, SubscriptionPaymentHandler[SUBSCRIPTION_ITEM_CATEGORY, SubscriptionPaymentData[Any]]],
    one_time_handlers: Dict[ONE_TIME_ITEM_CATEGORY, OneTimePaymentHandler[ONE_TIME_ITEM_CATEGORY, OneTimePaymentData[Any]]],
    enabled_providers: List[PaymentProvider]
) -> None:
    configure_creditor(app)
    init_services(enabled_providers, item_type_to_item_service, sub_handlers, one_time_handlers)



def webhook_configure(app: Flask, enabled_providers: List[PaymentProvider], forwarder: Forwarder) -> None:
    configure_webhook(app, enabled_providers, forwarder)

def configure_webhook_and_handler(
    app: Flask,
    item_type_to_item_service: Dict[ItemType, ItemCollectionService[Union[ONE_TIME_ITEM_CATEGORY, SUBSCRIPTION_ITEM_CATEGORY]]],
    sub_handlers: Dict[SUBSCRIPTION_ITEM_CATEGORY, SubscriptionPaymentHandler[SUBSCRIPTION_ITEM_CATEGORY, SubscriptionPaymentData[Any]]],
    one_time_handlers: Dict[ONE_TIME_ITEM_CATEGORY, OneTimePaymentHandler[ONE_TIME_ITEM_CATEGORY, OneTimePaymentData[Any]]],
    enabled_providers: List[PaymentProvider],
    forwarder: Forwarder
) -> None:
    webhook_configure(app, enabled_providers, forwarder)
    creditor_configure(app, item_type_to_item_service, sub_handlers, one_time_handlers, enabled_providers)

__all__ = [
    "configure_creditor",
    "configure_webhook",
    "PaymentHandler",
    "ItemCollectionService",
    "configure_webhook_and_handler",
    "SubscriptionPaymentData",
    "OneTimePaymentData",
]