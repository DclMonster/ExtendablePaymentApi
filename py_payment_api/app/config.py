from flask import Flask
from flask_restful import Api
import resources
from dotenv import load_dotenv
from .enums import PaymentProvider

def configure_webhook(app: Flask, enabled_providers: list[PaymentProvider]) -> None:
    """
    Configure the given Flask application.

    Parameters
    ----------
    app : Flask
        The Flask application to configure.
    enabled_providers : list[PaymentProvider]
        List of enabled payment providers.
    """
    # Load environment variables
    load_dotenv()

    # Initialize the API
    api = Api(app)

    # Conditionally register the webhook resources
    if PaymentProvider.COINBASE in enabled_providers:
        api.add_resource(resources.CoinbaseWebhook, '/webhook/coinbase')
    if PaymentProvider.APPLE in enabled_providers:
        api.add_resource(resources.AppleWebhook, '/webhook/apple')
    if PaymentProvider.GOOGLE in enabled_providers:
        api.add_resource(resources.GoogleWebhook, '/webhook/google')
    if PaymentProvider.PAYPAL in enabled_providers:
        api.add_resource(resources.PaypalWebhook, '/webhook/paypal')
    if PaymentProvider.COINSUB in enabled_providers:
        api.add_resource(resources.CoinSubWebhook, '/webhook/coinsub')
    


def configure_creditor(app: Flask) -> None:
    api = Api(app)
    api.add_resource(resources.PaymentFulfillment, '/fulfillment/payment')


