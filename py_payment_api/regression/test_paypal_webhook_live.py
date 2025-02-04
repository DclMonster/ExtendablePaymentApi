"""Live webhook regression tests for PayPal payment verification."""
import os
import pytest
import json
import time
import requests
from typing import Dict, Any, Generator, Optional
from flask import Flask, request
from flask.testing import FlaskClient
from threading import Thread
from ..app.verifiers.paypal_verifier import PayPalVerifier
from ..app.resources.webhook.paypal import PayPalWebhook
from ..app.services.forwarder.abstract.forwarder import Forwarder
from ..app.services.store.enum.item_type import ItemType
from werkzeug.serving import make_server

# Skip tests if required environment variables are not set
pytestmark = pytest.mark.skipif(
    not all([
        os.getenv('PAYPAL_CLIENT_ID'),
        os.getenv('PAYPAL_CLIENT_SECRET'),
        os.getenv('PAYPAL_WEBHOOK_URL'),  # URL where PayPal will send webhooks
        os.getenv('PAYPAL_SANDBOX_MODE'),
        os.getenv('PAYPAL_TEST_ORDER_ID')
    ]),
    reason="Missing required environment variables for PayPal live webhook tests"
)

class WebhookTestServer:
    """Test server to receive live webhooks."""
    
    def __init__(self, host: str = 'localhost', port: int = 5051) -> None:
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
def paypal_verifier() -> PayPalVerifier:
    """Create a PayPalVerifier instance for testing."""
    return PayPalVerifier()

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
def paypal_webhook(mock_forwarder: Forwarder) -> PayPalWebhook[ItemType]:
    """Create a PayPalWebhook instance for testing."""
    return PayPalWebhook[ItemType](forwarder=mock_forwarder)

@pytest.fixture
def test_order_data() -> Dict[str, Any]:
    """Sample order data for testing."""
    return {
        "intent": "CAPTURE",
        "purchase_units": [{
            "amount": {
                "currency_code": "USD",
                "value": "0.50"  # Small amount for testing
            },
            "description": "Live Webhook Test Product",
            "custom_id": "live_webhook_test_user"
        }],
        "application_context": {
            "return_url": "https://example.com/success",
            "cancel_url": "https://example.com/cancel"
        }
    }

@pytest.mark.live
@pytest.mark.regression
class TestPayPalLiveWebhook:
    """Live webhook regression tests for PayPal payment verification."""

    def test_webhook_registration(self, paypal_verifier: PayPalVerifier) -> None:
        """Test registering a webhook endpoint with PayPal."""
        # Get webhook URL from environment
        webhook_url = os.getenv('PAYPAL_WEBHOOK_URL')
        assert webhook_url is not None
        
        # Register webhook with PayPal API
        access_token = paypal_verifier.get_access_token()
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        webhook_data = {
            'url': webhook_url,
            'event_types': [
                {'name': 'PAYMENT.CAPTURE.COMPLETED'},
                {'name': 'PAYMENT.CAPTURE.DENIED'},
                {'name': 'CHECKOUT.ORDER.COMPLETED'}
            ]
        }
        
        api_base = 'https://api-m.sandbox.paypal.com' if os.getenv('PAYPAL_SANDBOX_MODE') == 'true' else 'https://api-m.paypal.com'
        response = requests.post(
            f'{api_base}/v1/notifications/webhooks',
            headers=headers,
            json=webhook_data
        )
        
        assert response.status_code in [200, 201]
        webhook_id = response.json()['id']
        assert webhook_id is not None

    def test_live_order_webhook(
        self, 
        webhook_server: WebhookTestServer,
        paypal_verifier: PayPalVerifier,
        test_order_data: Dict[str, Any]
    ) -> None:
        """Test receiving a live webhook for order events."""
        # Create a new order
        access_token = paypal_verifier.get_access_token()
        api_base = 'https://api-m.sandbox.paypal.com' if os.getenv('PAYPAL_SANDBOX_MODE') == 'true' else 'https://api-m.paypal.com'
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(
            f'{api_base}/v2/checkout/orders',
            headers=headers,
            json=test_order_data
        )
        
        assert response.status_code == 201
        order_id = response.json()['id']
        
        # Wait for webhook (timeout after 30 seconds)
        timeout = time.time() + 30
        received_order_webhook = False
        
        while time.time() < timeout and not received_order_webhook:
            for webhook in webhook_server.received_webhooks:
                if (
                    webhook.get('resource_type') == 'checkout-order' and
                    webhook.get('resource', {}).get('id') == order_id
                ):
                    received_order_webhook = True
                    break
            if not received_order_webhook:
                time.sleep(1)
        
        assert received_order_webhook, "Did not receive webhook for order creation"

    def test_live_webhook_signature(
        self,
        webhook_server: WebhookTestServer,
        paypal_verifier: PayPalVerifier,
        test_order_data: Dict[str, Any]
    ) -> None:
        """Test verifying signatures of live webhooks."""
        # Create a new order to trigger a webhook
        access_token = paypal_verifier.get_access_token()
        api_base = 'https://api-m.sandbox.paypal.com' if os.getenv('PAYPAL_SANDBOX_MODE') == 'true' else 'https://api-m.paypal.com'
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(
            f'{api_base}/v2/checkout/orders',
            headers=headers,
            json=test_order_data
        )
        
        assert response.status_code == 201
        
        # Wait for webhook (timeout after 30 seconds)
        timeout = time.time() + 30
        valid_signature = False
        
        while time.time() < timeout and not valid_signature:
            for webhook in webhook_server.received_webhooks:
                # Get the signature from the webhook headers
                if 'PAYPAL-TRANSMISSION-SIG' in request.headers:
                    try:
                        valid_signature = paypal_verifier.verify_signature(
                            webhook,
                            request.headers['PAYPAL-TRANSMISSION-SIG'],
                            request.headers['PAYPAL-TRANSMISSION-ID'],
                            request.headers['PAYPAL-TRANSMISSION-TIME']
                        )
                        if valid_signature:
                            break
                    except Exception:
                        continue
            if not valid_signature:
                time.sleep(1)
        
        assert valid_signature, "Did not receive webhook with valid signature"

    def test_live_webhook_processing(
        self,
        webhook_server: WebhookTestServer,
        paypal_webhook: PayPalWebhook[ItemType],
        mock_forwarder: Forwarder,
        test_order_data: Dict[str, Any]
    ) -> None:
        """Test processing of live webhooks."""
        # Get test order ID from environment
        test_order_id = os.getenv('PAYPAL_TEST_ORDER_ID')
        assert test_order_id is not None
        
        # Wait for webhook and process it (timeout after 30 seconds)
        timeout = time.time() + 30
        processed_webhook = False
        
        while time.time() < timeout and not processed_webhook:
            for webhook_data in webhook_server.received_webhooks:
                if webhook_data.get('resource', {}).get('id') == test_order_id:
                    # Process the webhook
                    try:
                        webhook_result = paypal_webhook.parse_event_data(json.dumps(webhook_data))
                        assert webhook_result is not None
                        assert webhook_result['transaction_id'] == test_order_id
                        assert webhook_result['user_id'] == test_order_data['purchase_units'][0]['custom_id']
                        processed_webhook = True
                        break
                    except Exception:
                        continue
            if not processed_webhook:
                time.sleep(1)
        
        assert processed_webhook, "Failed to process live webhook"

    def test_live_webhook_status_transition(
        self,
        webhook_server: WebhookTestServer,
        paypal_webhook: PayPalWebhook[ItemType],
        test_order_data: Dict[str, Any]
    ) -> None:
        """Test webhook status transitions in live environment."""
        # Create a new order
        access_token = paypal_verifier.get_access_token()
        api_base = 'https://api-m.sandbox.paypal.com' if os.getenv('PAYPAL_SANDBOX_MODE') == 'true' else 'https://api-m.paypal.com'
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(
            f'{api_base}/v2/checkout/orders',
            headers=headers,
            json=test_order_data
        )
        
        assert response.status_code == 201
        order_id = response.json()['id']
        
        # Track status transitions
        received_statuses = set()
        timeout = time.time() + 30
        
        while time.time() < timeout and len(received_statuses) < 2:  # Wait for at least 2 different statuses
            for webhook_data in webhook_server.received_webhooks:
                if webhook_data.get('resource', {}).get('id') == order_id:
                    try:
                        webhook_result = paypal_webhook.parse_event_data(json.dumps(webhook_data))
                        if webhook_result and webhook_result['status']:
                            received_statuses.add(webhook_result['status'])
                    except Exception:
                        continue
            if len(received_statuses) < 2:
                time.sleep(1)
        
        assert len(received_statuses) >= 2, "Did not receive multiple status transitions"
        assert 'webhook_recieved' in received_statuses, "Missing initial webhook_received status"

    def test_sandbox_api_integration(self, paypal_verifier: PayPalVerifier) -> None:
        """Test PayPal sandbox API integration."""
        # Ensure sandbox mode is enabled
        assert os.getenv('PAYPAL_SANDBOX_MODE') == 'true', "Sandbox mode must be enabled for regression tests"
        
        # Test access token generation
        access_token = paypal_verifier.get_access_token()
        assert access_token is not None
        
        # Test order verification
        test_order_id = os.getenv('PAYPAL_TEST_ORDER_ID')
        assert test_order_id is not None
        
        api_base = 'https://api-m.sandbox.paypal.com'
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(
            f'{api_base}/v2/checkout/orders/{test_order_id}',
            headers=headers
        )
        
        assert response.status_code == 200
        order_data = response.json()
        assert order_data['id'] == test_order_id 