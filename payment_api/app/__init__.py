from .config import configure_app
from flask import Flask
from .services.subscription.handlers.subscription_handler import SubscriptionHandler

def api_configure(app: Flask, subscription_handlers: SubscriptionHandler) -> None:
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
    

    # Additional configuration can be added here if needed

# Example usage
# app = Flask(__name__)
# api_configure(app)

