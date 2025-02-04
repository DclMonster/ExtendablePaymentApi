"""Live webhook regression tests for Google Play payment verification."""
import os
import pytest
import json
import time
import requests
from typing import Dict, Any, Generator, Optional
from flask import Flask, request
from flask.testing import FlaskClient
from threading import Thread
from ..app.verifiers.google_verifier import GoogleVerifier
from ..app.resources.webhook.google import GoogleWebhook
from ..app.services.forwarder.abstract.forwarder import Forwarder
from ..app.services.store.enum.item_type import ItemType
from werkzeug.serving import make_server

# Skip tests if required environment variables are not set
pytestmark = pytest.mark.skipif(
    not all([
        os.getenv('GOOGLE_PUBLIC_KEY'),
        os.getenv('GOOGLE_PACKAGE_NAME'),
        os.getenv('GOOGLE_SERVICE_ACCOUNT_KEY'),
        os.getenv('GOOGLE_SANDBOX_MODE'),
        os.getenv('GOOGLE_TEST_PURCHASE_TOKEN'),
        os.getenv('GOOGLE_TEST_PRODUCT_ID')
    ]),
    reason="Missing required environment variables for Google Play live webhook tests"
)

class WebhookTestServer:
    """Test server to receive live webhooks."""
    
    def __init__(self, host: str = 'localhost', port: int = 5052) -> None:
        """Initialize the test server.
        
        Parameters
        ----------
        host : str
            The host to bind to
        port : int
            The port to listen on
        """
        self.host = host
        self.port = port
        self.received_webhooks: list[Dict[str, Any]] = []
        self.app = Flask(__name__)
        self.server: Optional[Any] = None
        self.thread: Optional[Thread] = None
        
        # Register webhook endpoint
        @self.app.route('/webhook', methods=['POST'])
        def webhook() -> tuple[Dict[str, str], int]:
            if request.is_json:
                webhook_data = request.get_json()
                self.received_webhooks.append(webhook_data)
                return {"message": "Webhook received"}, 200
            return {"error": "Invalid JSON"}, 400
    
    def start(self) -> None:
        """Start the test server in a separate thread."""
        self.server = make_server(self.host, self.port, self.app)
        self.thread = Thread(target=self.server.serve_forever)
        self.thread.daemon = True
        self.thread.start()
    
    def stop(self) -> None:
        """Stop the test server."""
        if self.server:
            self.server.shutdown()
        if self.thread:
            self.thread.join()

@pytest.fixture(scope="session")
def webhook_server() -> Generator[WebhookTestServer, None, None]:
    """Create and run a webhook test server."""
    server = WebhookTestServer()
    server.start()
    yield server
    server.stop()

@pytest.fixture
def google_verifier() -> GoogleVerifier:
    """Create a GoogleVerifier instance for testing."""
    return GoogleVerifier()

@pytest.fixture
def mock_forwarder() -> Forwarder:
    """Create a mock forwarder for testing."""
    class MockForwarder(Forwarder):
        def __init__(self) -> None:
            self.received_events: list[Dict[str, Any]] = []
            
        def forward_event(self, event_data: Dict[str, Any]) -> None:
            self.received_events.append(event_data)
            print(f"Forwarding event: {event_data}")
    return MockForwarder()

@pytest.fixture
def google_webhook(mock_forwarder: Forwarder) -> GoogleWebhook[ItemType]:
    """Create a GoogleWebhook instance for testing."""
    return GoogleWebhook[ItemType](forwarder=mock_forwarder)

@pytest.mark.live
@pytest.mark.regression
class TestGooglePlayLiveWebhook:
    """Live webhook regression tests for Google Play payment verification."""

    def test_sandbox_purchase_verification(self, google_verifier: GoogleVerifier) -> None:
        """Test verifying a purchase in sandbox mode."""
        # Ensure sandbox mode is enabled
        assert os.getenv('GOOGLE_SANDBOX_MODE') == 'true', "Sandbox mode must be enabled for regression tests"
        
        # Get test data from environment
        purchase_token = os.getenv('GOOGLE_TEST_PURCHASE_TOKEN')
        product_id = os.getenv('GOOGLE_TEST_PRODUCT_ID')
        assert purchase_token is not None
        assert product_id is not None
        
        # Verify the purchase
        purchase_data = google_verifier.verify_purchase(purchase_token, product_id)
        assert purchase_data is not None
        assert purchase_data.get('orderId') is not None
        assert purchase_data.get('purchaseState') in [0, 1, 2]  # 0: Purchased, 1: Canceled, 2: Pending

    def test_sandbox_subscription_verification(self, google_verifier: GoogleVerifier) -> None:
        """Test verifying a subscription in sandbox mode."""
        # Get test data from environment
        purchase_token = os.getenv('GOOGLE_TEST_PURCHASE_TOKEN')
        product_id = os.getenv('GOOGLE_TEST_PRODUCT_ID')
        assert purchase_token is not None
        assert product_id is not None
        
        # Verify the subscription
        subscription_data = google_verifier.verify_purchase(purchase_token, product_id, True)
        assert subscription_data is not None
        assert subscription_data.get('orderId') is not None
        assert 'autoRenewing' in subscription_data

    def test_sandbox_purchase_acknowledgment(self, google_verifier: GoogleVerifier) -> None:
        """Test acknowledging a purchase in sandbox mode."""
        # Get test data from environment
        purchase_token = os.getenv('GOOGLE_TEST_PURCHASE_TOKEN')
        product_id = os.getenv('GOOGLE_TEST_PRODUCT_ID')
        assert purchase_token is not None
        assert product_id is not None
        
        # Acknowledge the purchase
        result = google_verifier.acknowledge_purchase(purchase_token, product_id)
        assert result is True

    def test_sandbox_voided_purchases(self, google_verifier: GoogleVerifier) -> None:
        """Test retrieving voided purchases in sandbox mode."""
        # Get voided purchases
        voided_purchases = google_verifier.get_voided_purchases()
        assert isinstance(voided_purchases, list)

    def test_live_webhook_processing(
        self,
        webhook_server: WebhookTestServer,
        google_webhook: GoogleWebhook[ItemType],
        mock_forwarder: Forwarder
    ) -> None:
        """Test processing of live webhooks."""
        # Create test webhook data
        test_data = {
            "message": {
                "data": {
                    "oneTimeProductNotification": {
                        "orderId": os.getenv('GOOGLE_TEST_PURCHASE_TOKEN'),
                        "productId": os.getenv('GOOGLE_TEST_PRODUCT_ID'),
                        "purchaseToken": os.getenv('GOOGLE_TEST_PURCHASE_TOKEN'),
                        "notificationType": "ONE_TIME_PRODUCT_PURCHASED"
                    }
                }
            }
        }
        
        # Process the webhook
        webhook_data = google_webhook.parse_event_data(json.dumps(test_data))
        assert webhook_data is not None
        assert webhook_data['transaction_id'] == os.getenv('GOOGLE_TEST_PURCHASE_TOKEN')
        assert webhook_data['product_id'] == os.getenv('GOOGLE_TEST_PRODUCT_ID')
        assert webhook_data['status'] == 'paid'

    def test_live_webhook_signature(
        self,
        webhook_server: WebhookTestServer,
        google_verifier: GoogleVerifier
    ) -> None:
        """Test verifying signatures of live webhooks."""
        # Create test data
        test_data = {
            "message": {
                "data": {
                    "oneTimeProductNotification": {
                        "orderId": os.getenv('GOOGLE_TEST_PURCHASE_TOKEN')
                    }
                }
            }
        }
        
        # Create signature using test key
        signature = google_verifier._create_test_signature(json.dumps(test_data))
        
        # Verify signature
        assert google_verifier.verify_signature(test_data, signature)

    def test_live_webhook_status_transition(
        self,
        webhook_server: WebhookTestServer,
        google_webhook: GoogleWebhook[ItemType]
    ) -> None:
        """Test webhook status transitions in live environment."""
        # Create test data for different statuses
        status_data = [
            ("ONE_TIME_PRODUCT_PURCHASED", "paid"),
            ("SUBSCRIPTION_PURCHASED", "paid"),
            ("SUBSCRIPTION_CANCELED", "sent_to_processor"),
            ("SUBSCRIPTION_ON_HOLD", "sent_to_processor")
        ]
        
        for notification_type, expected_status in status_data:
            test_data = {
                "message": {
                    "data": {
                        "oneTimeProductNotification": {
                            "orderId": os.getenv('GOOGLE_TEST_PURCHASE_TOKEN'),
                            "notificationType": notification_type
                        }
                    }
                }
            }
            
            webhook_data = google_webhook.parse_event_data(json.dumps(test_data))
            assert webhook_data['status'] == expected_status 