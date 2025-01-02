from typing import Callable, Dict, TypedDict, List
from ..enums import PaymentProvider
from ..services.subscription.abstract.subscription_serrvice import SubscriptionService, BaseSubscriptionData
from ..services.subscription.handlers.subscription_handler import SubscriptionHandler
from ..services.payment.payment_handler import PaymentHandler, BasePaymentData
from ..services.payment.available_item import AvailableItem
class AppleData(TypedDict):
    """
    Represents the data structure for Apple payment events.
    """
    transaction_id: str
    amount: float
    currency: str
    status: str

class GoogleData(TypedDict):
    """
    Represents the data structure for Google payment events.
    """
    transaction_id: str
    amount: float
    currency: str
    status: str 

class CoinbaseData(TypedDict):
    """
    Represents the data structure for Coinbase payment events.
    """
    transaction_id: str
    amount: float
    currency: str
    status: str

class PaypalData(TypedDict):
    """
    Represents the data structure for Paypal payment events.
    """
    transaction_id: str
    amount: float
    currency: str
    status: str

class CoinSubData(TypedDict):
    """
    Represents the data structure for CoinSub payment events.
    """
    transaction_id: str
    amount: float
    currency: str
    status: str

class PaymentService:
    """
    Service class for registering and executing actions based on different payment providers.
    """


    apple_payment_handlers: List[PaymentHandler[AppleData]]
    google_payment_handlers: List[PaymentHandler[GoogleData]]
    coinbase_payment_handlers: List[PaymentHandler[CoinbaseData]]
    paypal_payment_handlers: List[PaymentHandler[PaypalData]]
    coinsub_payment_handlers: List[PaymentHandler[CoinSubData]]


    def __init__(self) -> None:
        self.apple_payment_handlers = []
        self.google_payment_handlers = []
        self.coinbase_payment_handlers = []
        self.paypal_payment_handlers = []
        self.coinsub_payment_handlers = []

    def register_paypal_payment_handler(self, handler: PaymentHandler[PaypalData]):
        self.paypal_payment_handlers.append(handler)

    def register_coinsub_payment_handler(self, handler: PaymentHandler[CoinSubData]):
        self.coinsub_payment_handlers.append(handler)

    def register_apple_payment_handler(self, handler: PaymentHandler[AppleData]):
        self.apple_payment_handlers.append(handler)

    def register_google_payment_handler(self, handler: PaymentHandler[GoogleData]):
        self.google_payment_handlers.append(handler)

    def register_coinbase_payment_handler(self, handler: PaymentHandler[CoinbaseData]):
        self.coinbase_payment_handlers.append(handler)

    def on_apple_payment(self, payment: AppleData):
        for handler in self.apple_payment_handlers:
            handler.onPayment(payment)

    def on_google_payment(self, payment: GoogleData):
        for handler in self.google_payment_handlers:
            handler.onPayment(payment)

    def on_coinbase_payment(self, payment: CoinbaseData):
        for handler in self.coinbase_payment_handlers:
            handler.onPayment(payment)

    def on_paypal_payment(self, payment: PaypalData):
        for handler in self.paypal_payment_handlers:
            handler.onPayment(payment)

    def on_coinsub_payment(self, payment: CoinSubData):
        for handler in self.coinsub_payment_handlers:
            handler.onPayment(payment)

    def get_items(self) -> Dict[str, List[AvailableItem]]:
        result = {}
        result[PaymentProvider.APPLE.value] = []
        for handler in self.apple_payment_handlers:
            result[PaymentProvider.APPLE.value].extend(handler.get_items())
        result[PaymentProvider.GOOGLE.value] = []
        for handler in self.google_payment_handlers:
            result[PaymentProvider.GOOGLE.value].extend(handler.get_items())
        result[PaymentProvider.COINBASE.value] = []
        for handler in self.coinbase_payment_handlers:
            result[PaymentProvider.COINBASE.value].extend(handler.get_items())
        result[PaymentProvider.PAYPAL.value] = []
        for handler in self.paypal_payment_handlers:
            result[PaymentProvider.PAYPAL.value].extend(handler.get_items())
        result[PaymentProvider.COINSUB.value] = []
        for handler in self.coinsub_payment_handlers:
            result[PaymentProvider.COINSUB.value].extend(handler.get_items())
        return result

