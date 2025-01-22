from flask import Flask
from flask_restful import Api
from .resources import CoinbaseWebhook, AppleWebhook, GoogleWebhook, PaypalWebhook, CoinSubWebhook, CreditPurchase
from dotenv import load_dotenv  # type: ignore
from .services import PaymentProvider, get_services, Services
from typing import List, Any
from .services.forwarder.abstract.forwarder import Forwarder
import os

def configure_webhook(app: Flask, enabled_providers: List[PaymentProvider], forwarder: Forwarder) -> None:
    """
    Configure the given Flask application.

    Parameters
    ----------
    app : Flask
        The Flask application to configure.
    enabled_providers : List[PaymentProvider]
        List of enabled payment providers.
    """
    # Load environment variables
    load_dotenv()

    # Initialize the API and services
    api: Api = Api(app)

    # Conditionally register the webhook resources
    if PaymentProvider.COINBASE in enabled_providers:
        api.add_resource(CoinbaseWebhook, '/webhook/coinbase', endpoint='webhook.coinbase', resource_class_kwargs={'forwarder': forwarder})
    if PaymentProvider.APPLE in enabled_providers:
        api.add_resource(AppleWebhook, '/webhook/apple', endpoint='webhook.apple', resource_class_kwargs={'forwarder': forwarder})
    if PaymentProvider.GOOGLE in enabled_providers:
        api.add_resource(GoogleWebhook, '/webhook/google', endpoint='webhook.google', resource_class_kwargs={'forwarder': forwarder})
    if PaymentProvider.PAYPAL in enabled_providers:
        api.add_resource(PaypalWebhook, '/webhook/paypal', endpoint='webhook.paypal', resource_class_kwargs={'forwarder': forwarder})
    if PaymentProvider.COINSUB in enabled_providers:
        api.add_resource(CoinSubWebhook, '/webhook/coinsub', endpoint='webhook.coinsub', resource_class_kwargs={'forwarder': forwarder})

def configure_creditor(app: Flask) -> None:
    api: Api = Api(app)
    api.add_resource(CreditPurchase, '/creditor/transaction', endpoint='creditor.process_payment')


