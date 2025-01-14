import pytest
from flask import Flask
from .. import configure_app, configure_creditor, configure_webhook

@pytest.fixture
def app():
    return Flask(__name__)

def test_configure_app(app):
    configure_app(app)
    # Add assertions to verify app configuration
    assert app.config['DEBUG'] is True

def test_configure_creditor(app):
    configure_creditor(app)
    # Add assertions to verify creditor configuration
    assert 'creditor_endpoint' in app.url_map._rules_by_endpoint

def test_configure_webhook(app):
    configure_webhook(app)
    # Add assertions to verify webhook configuration
    assert 'webhook_endpoint' in app.url_map._rules_by_endpoint 