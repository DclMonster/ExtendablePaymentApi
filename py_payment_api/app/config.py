from flask import Flask
from flask_restful import Api
import resources
from dotenv import load_dotenv

def configure_webhook(app: Flask) -> None:
    """
    Configure the given Flask application.

    Parameters
    ----------
    app : Flask
        The Flask application to configure.
    """
    # Load environment variables
    load_dotenv()

    # Initialize the API
    api = Api(app)

    # Register the webhook resources
    api.add_resource(resources.CoinbaseWebhook, '/webhook/coinbase')
    api.add_resource(resources.AppleWebhook, '/webhook/apple')
    api.add_resource(resources.GoogleWebhook, '/webhook/google')
    api.add_resource(resources.PaypalWebhook, '/webhook/paypal')
    api.add_resource(resources.CoinSubWebhook, '/webhook/coinsub')
    


def configure_creditor(app: Flask) -> None:
    api = Api(app)
    api.add_resource(resources.PaymentFulfillment, '/fulfillment/payment')


