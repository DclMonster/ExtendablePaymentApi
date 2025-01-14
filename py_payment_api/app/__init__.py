from .config import configure_app, configure_creditor, configure_webhook
from flask import Flask
from .services.subscription.handlers.subscription_handler import SubscriptionHandler
from typing import List
from .services.subscription.apple_subscription_service import AppleSubscriptionData
from .services.subscription.google_subscription_service import GoogleSubscriptionData
from .services.subscription.paypal_subscription_service import PaypalSubscriptionData
from .services.subscription.coinsub_subscription_service import CoinSubScriptionData
from .services.payment_service import (
    AppleData,
    GoogleData,
    PaypalData,
    CoinbaseData,
    CoinSubData,
)
from .services.payment import PaymentHandler
from .services import (
    apple_subscription_service,
    google_subscription_service,
    paypal_subscription_service,
    coinsub_subscription_service,
    all_payment_service,
)
from .enums import PaymentProvider

def creditor_configure(
    app: Flask,
    handlers: dict[PaymentProvider, List[SubscriptionHandler | PaymentHandler]]
) -> None:
    configure_creditor(app)
    for provider, handler_list in handlers.items():
        if provider == PaymentProvider.APPLE:
            for handler in handler_list:
                if isinstance(handler, SubscriptionHandler):
                    apple_subscription_service.register_handler(handler)
                elif isinstance(handler, PaymentHandler):
                    all_payment_service.register_apple_payment_handler(handler)
        elif provider == PaymentProvider.GOOGLE:
            for handler in handler_list:
                if isinstance(handler, SubscriptionHandler):
                    google_subscription_service.register_handler(handler)
                elif isinstance(handler, PaymentHandler):
                    all_payment_service.register_google_payment_handler(handler)
        elif provider == PaymentProvider.PAYPAL:
            for handler in handler_list:
                if isinstance(handler, SubscriptionHandler):
                    paypal_subscription_service.register_handler(handler)
                elif isinstance(handler, PaymentHandler):
                    all_payment_service.register_paypal_payment_handler(handler)
        elif provider == PaymentProvider.COINSUB:
            for handler in handler_list:
                if isinstance(handler, SubscriptionHandler):
                    coinsub_subscription_service.register_handler(handler)
                elif isinstance(handler, PaymentHandler):
                    all_payment_service.register_coinsub_payment_handler(handler)
        elif provider == PaymentProvider.COINBASE:
            for handler in handler_list:
                if isinstance(handler, PaymentHandler):
                    all_payment_service.register_coinbase_payment_handler(handler)


def webhook_configure(app: Flask, enabled_providers: list[PaymentProvider]) -> None:
    configure_webhook(app, enabled_providers)

def configure_webhook_and_handler(
    app: Flask,
    handlers: dict[PaymentProvider, List[SubscriptionHandler | PaymentHandler]],
    enabled_providers: list[PaymentProvider]
) -> None:
    webhook_configure(app, enabled_providers)
    for provider, handler_list in handlers.items():
        if provider == PaymentProvider.APPLE:
            for handler in handler_list:
                if isinstance(handler, SubscriptionHandler):
                    apple_subscription_service.register_handler(handler)
                elif isinstance(handler, PaymentHandler):
                    all_payment_service.register_apple_payment_handler(handler)
        elif provider == PaymentProvider.GOOGLE:
            for handler in handler_list:
                if isinstance(handler, SubscriptionHandler):
                    google_subscription_service.register_handler(handler)
                elif isinstance(handler, PaymentHandler):
                    all_payment_service.register_google_payment_handler(handler)
        elif provider == PaymentProvider.PAYPAL:
            for handler in handler_list:
                if isinstance(handler, SubscriptionHandler):
                    paypal_subscription_service.register_handler(handler)
                elif isinstance(handler, PaymentHandler):
                    all_payment_service.register_paypal_payment_handler(handler)
        elif provider == PaymentProvider.COINSUB:
            for handler in handler_list:
                if isinstance(handler, SubscriptionHandler):
                    coinsub_subscription_service.register_handler(handler)
                elif isinstance(handler, PaymentHandler):
                    all_payment_service.register_coinsub_payment_handler(handler)
        elif provider == PaymentProvider.COINBASE:
            for handler in handler_list:
                if isinstance(handler, PaymentHandler):
                    all_payment_service.register_coinbase_payment_handler(handler)

def __configure_payment_api(
    app: Flask,
    apple_sub_handlers: List[SubscriptionHandler[AppleSubscriptionData]],
    google_sub_handlers: List[SubscriptionHandler[GoogleSubscriptionData]],
    paypal_sub_handlers: List[SubscriptionHandler[PaypalSubscriptionData]],
    coinsub_sub_handlers: List[SubscriptionHandler[CoinSubScriptionData]],
    apple_payment_handlers: List[PaymentHandler[AppleData]],
    google_payment_handlers: List[PaymentHandler[GoogleData]],
    paypal_payment_handlers: List[PaymentHandler[PaypalData]],
    coinsub_payment_handlers: List[PaymentHandler[CoinSubData]],
    coinbase_payment_handlers: List[PaymentHandler[CoinbaseData]],
) -> None:
    """
    Configures the Flask app with routes and configurations for payments and subscriptions.

    Parameters
    ----------
    app : Flask
        The Flask application instance to configure.
    """
    # Call configure_app to apply configurations
    configure_creditor(app)

    # Mapping of subscription handlers to their respective registration functions
    subscription_mapping = {
        apple_sub_handlers: apple_subscription_service.register_handler,
        google_sub_handlers: google_subscription_service.register_handler,
        paypal_sub_handlers: paypal_subscription_service.register_handler,
        coinsub_sub_handlers: coinsub_subscription_service.register_handler,
    }

    # Register subscription handlers
    for handlers, register_func in subscription_mapping.items():
        for handler in handlers:
            register_func(handler)

    # Mapping of payment handlers to their respective registration functions
    payment_mapping = {
        apple_payment_handlers: all_payment_service.register_apple_payment_handler,
        google_payment_handlers: all_payment_service.register_google_payment_handler,
        paypal_payment_handlers: all_payment_service.register_paypal_payment_handler,
        coinsub_payment_handlers: all_payment_service.register_coinsub_payment_handler,
        coinbase_payment_handlers: all_payment_service.register_coinbase_payment_handler,
    }

    # Register payment handlers
    for handlerss, register_funcc in payment_mapping.items():
        for handlerr in handlerss:
            register_funcc(handlerr)

__all__ = [
    "configure_creditor",
    "configure_webhook",
    "PaymentHandler",
    "AppleData",
    "GoogleData",
    "PaypalData",
    "CoinbaseData",
    "CoinSubData",
    "AppleSubscriptionData",
    "GoogleSubscriptionData",
    "PaypalSubscriptionData",
    "CoinSubScriptionData",
]