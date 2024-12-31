from .config import configure_app
from flask import Flask
from .services.subscription.handlers.subscription_handler import SubscriptionHandler
from typing import List
from .services.subscription.apple_subscription_service import AppleSubscriptionData
from .services.subscription.google_subscription_service import GoogleSubscriptionData
from .services.subscription.paypal_subscription_service import PaypalSubscriptionData
from .services.subscription.coinsub_subscription_service import CoinSubScriptionData
from .services.payment_service import AppleData, GoogleData, PaypalData, CoinbaseData, CoinSubData
from .services.payment import PaymentHandler
from .services import apple_subscription_service, google_subscription_service, paypal_subscription_service, coinsub_subscription_service, all_payment_service

def api_configure(
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
    subscription_handlers : dict, optional
        A dictionary of subscription handlers to configure, by default None
    """
    # Call configure_app to apply configurations
    configure_app(app)

    # Configure subscription handlers if provided
    for handler in apple_sub_handlers:
        apple_subscription_service.register_handler(handler)
    for handler in google_sub_handlers:
        google_subscription_service.register_handler(handler)
    for handler in paypal_sub_handlers:
        paypal_subscription_service.register_handler(handler)
    for handler in coinsub_sub_handlers:
        coinsub_subscription_service.register_handler(handler)

    for handler in apple_payment_handlers:
        all_payment_service.register_apple_payment_handler(handler)
    for handler in google_payment_handlers:
        all_payment_service.register_google_payment_handler(handler)
    for handler in paypal_payment_handlers:
        all_payment_service.register_paypal_payment_handler(handler)
    for handler in coinsub_payment_handlers:
        all_payment_service.register_coinsub_payment_handler(handler)
    for handler in coinbase_payment_handlers:
        all_payment_service.register_coinbase_payment_handler(handler)
    # Additional configuration can be added here if needed


# Example usage
# app = Flask(__name__)
# api_configure(app)
