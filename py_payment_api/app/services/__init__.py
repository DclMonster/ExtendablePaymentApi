from .services import (
    all_payment_service,
    apple_subscription_service,
    google_subscription_service,
    paypal_subscription_service,
    coinsub_subscription_service,
)
from .subscription.apple_subscription_service import AppleSubscriptionData
from .subscription.google_subscription_service import GoogleSubscriptionData
from .subscription.paypal_subscription_service import PaypalSubscriptionData
from .subscription.coinsub_subscription_service import CoinSubScriptionData
from .subscription.apple_subscription_service import AppleSubscriptionService
from .subscription.google_subscription_service import GoogleSubscriptionService
from .subscription.paypal_subscription_service import PaypalSubscriptionService
from .subscription.coinsub_subscription_service import CoinsubSubscriptionService

from .payment_service import AppleData, GoogleData, PaypalData, CoinbaseData, CoinSubData
from typing import TypeVar, Generic, List
from .store.services import construct_store_service
from enum import StrEnum
from .store.store_service import StoreService
from .payment_service import PaymentService
from .store.items import AvailableItem
from .payment_service import PaymentData

class PaymentProvider(StrEnum):
    APPLE = "apple"
    GOOGLE = "google"
    PAYPAL = "paypal"
    COINBASE = "coinbase"
    COINSUB = "coinsub"

ITEM_CATEGORY = TypeVar('ITEM_CATEGORY', bound=StrEnum)
class Services(Generic[ITEM_CATEGORY]):
    __store_service: StoreService[ITEM_CATEGORY]
    __payment_service: PaymentService
    __apple_subscription_service: AppleSubscriptionService
    __google_subscription_service: GoogleSubscriptionService
    __paypal_subscription_service: PaypalSubscriptionService
    __coinsub_subscription_service: CoinsubSubscriptionService
    def __init__(self):
        self.__store_service = construct_store_service[ITEM_CATEGORY]()
        self.__payment_service = PaymentService()
        self.__apple_subscription_service = AppleSubscriptionService()
        self.__google_subscription_service = GoogleSubscriptionService()
        self.__paypal_subscription_service = PaypalSubscriptionService()
        self.__coinsub_subscription_service = CoinsubSubscriptionService()


    def  get_items(self, item_category: ITEM_CATEGORY) -> list[AvailableItem]:
        return self.__store_service.get_items(item_category)
    
    def get_all_items(self) -> List[AvailableItem]:
        return self.__store_service.get_all_items()
    
    def on_apple_payment(self, payment_data: AppleData):
        self.__payment_service.on_apple_payment(payment_data)

    def on_google_payment(self, payment_data: GoogleData):
        self.__payment_service.on_google_payment(payment_data)

    def on_paypal_payment(self, payment_data: PaypalData):
        self.__payment_service.on_paypal_payment(payment_data)

    def on_coinbase_payment(self, payment_data: CoinbaseData):
        self.__payment_service.on_coinbase_payment(payment_data)

    def on_coinsub_payment(self, payment_data: CoinSubData):
        self.__payment_service.on_coinsub_payment(payment_data)

    def add_apple_subscription(self, subscription_data: AppleSubscriptionData):
        self.__apple_subscription_service.add_subscription(subscription_data)

    def add_google_subscription(self, subscription_data: GoogleSubscriptionData):
        self.__google_subscription_service.add_subscription(subscription_data)

    def add_paypal_subscription(self, subscription_data: PaypalSubscriptionData):
        self.__paypal_subscription_service.add_subscription(subscription_data)

    def add_coinsub_subscription(self, subscription_data: CoinSubScriptionData):
        self.__coinsub_subscription_service.add_subscription(subscription_data)

    def remove_apple_subscription(self, user_id: str):
        self.__apple_subscription_service.remove_subscription(user_id)

    def remove_google_subscription(self, user_id: str):
        self.__google_subscription_service.remove_subscription(user_id)

    def remove_paypal_subscription(self, user_id: str):
        self.__paypal_subscription_service.remove_subscription(user_id)

    def remove_coinsub_subscription(self, user_id: str):
        self.__coinsub_subscription_service.remove_subscription(user_id)

    def get_apple_subscriptions(self, user_id: str) -> List[AppleSubscriptionData]:
        return self.__apple_subscription_service.get_subscriptions(user_id)

    def get_google_subscriptions(self, user_id: str) -> List[GoogleSubscriptionData]:
        return self.__google_subscription_service.get_subscriptions(user_id)

    def get_paypal_subscriptions(self, user_id: str) -> List[PaypalSubscriptionData]:
        return self.__paypal_subscription_service.get_subscriptions(user_id)

    def get_coinsub_subscriptions(self, user_id: str) -> List[CoinSubScriptionData]:
        return self.__coinsub_subscription_service.get_subscriptions(user_id)
    
    def register_apple_subscription_handler(self, handler: AppleSubscriptionHandler):
        self.__apple_subscription_service.register_handler(handler)

    def register_google_subscription_handler(self, handler: GoogleSubscriptionHandler):
        self.__google_subscription_service.register_handler(handler)

    def register_paypal_subscription_handler(self, handler: PaypalSubscriptionHandler):
        self.__paypal_subscription_service.register_handler(handler)

    def register_coinsub_subscription_handler(self, handler: CoinsubSubscriptionHandler):
        self.__coinsub_subscription_service.register_handler(handler)



def init_services() -> Services[ITEM_CATEGORY]:
    return Services[ITEM_CATEGORY]()

__all__ = [
    'init_services',
    'Services',
    'PaymentProvider',
    "AppleSubscriptionData",
    "GoogleSubscriptionData",
    "PaypalSubscriptionData",
    "CoinSubScriptionData",
    "AppleData",
    "GoogleData",
    "PaypalData",
    "CoinbaseData",
    "CoinSubData",
]
