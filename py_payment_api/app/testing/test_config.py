import pytest
from flask import Flask
from ..services.store.enum.payment_provider import PaymentProvider
from ..config import configure_creditor, configure_webhook
from ..services.forwarder import WebSocketForwarder
@pytest.fixture
def app() -> Flask:
    app = Flask(__name__)
    app.config.update({
        'DEBUG': True,
        'TESTING': False,
        'JSON_SORT_KEYS': True,
        'JSONIFY_PRETTYPRINT_REGULAR': False
    })
    return app

def test_app_config(app: Flask) -> None:
    """Test application configuration."""
    assert app.config['DEBUG'] is True
    assert app.config['TESTING'] is False
    assert app.config['JSON_SORT_KEYS'] is True
    assert app.config['JSONIFY_PRETTYPRINT_REGULAR'] is False

def test_configure_creditor(app: Flask) -> None:
    """Test creditor configuration."""
    configure_creditor(app)
    # Check if creditor endpoints are registered
    rules = [rule.endpoint for rule in app.url_map.iter_rules()]
    assert 'creditor.process_payment' in rules
    assert 'creditor.get_transaction' in rules
    assert 'creditor.list_transactions' in rules

def test_configure_webhook(app: Flask) -> None:
    """Test webhook configuration."""
    enabled_providers = [
        PaymentProvider.PAYPAL,
        PaymentProvider.GOOGLE,
        PaymentProvider.COINBASE,
        PaymentProvider.APPLE,
        PaymentProvider.COINSUB
    ]
    forwarder = WebSocketForwarder()
    configure_webhook(app, enabled_providers, forwarder)
    # Check if webhook endpoints are registered
    rules = [rule.endpoint for rule in app.url_map.iter_rules()]
    assert 'webhook.paypal' in rules
    assert 'webhook.google' in rules
    assert 'webhook.coinbase' in rules
    assert 'webhook.apple' in rules
    assert 'webhook.coinsub' in rules 