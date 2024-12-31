from flask import Flask
from flask_restful import Api
from .resources.coinbase import CoinbaseWebhook
from .resources.apple import AppleWebhook
from .resources.google import GoogleWebhook
from dotenv import load_dotenv

def configure_app(app: Flask):
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
    api.add_resource(CoinbaseWebhook, '/webhook/coinbase')
    api.add_resource(AppleWebhook, '/webhook/apple')
    api.add_resource(GoogleWebhook, '/webhook/google') 