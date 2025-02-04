"""Live webhook regression tests for Coinbase payment verification."""
import os
import pytest
import json
import time
import requests
from typing import Dict, Any, Generator, Optional
from flask import Flask, request
from flask.testing import FlaskClient
from threading import Thread
from ..app.verifiers.coinbase_verifier import CoinbaseVerifier
from ..app.resources.webhook.coinbase import CoinbaseWebhook
from ..app.services.forwarder.abstract.forwarder import Forwarder
from ..app.services.store.enum.item_type import ItemType
from werkzeug.serving import make_server

# Skip tests if required environment variables are not set
pytestmark = pytest.mark.skipif(
    not all([
        os.getenv('COINBASE_API_KEY'),
        os.getenv('COINBASE_SECRET'),
        os.getenv('COINBASE_WEBHOOK_URL'),  # URL where Coinbase will send webhooks
        os.getenv('COINBASE_SANDBOX_MODE')
    ]),
    reason="Missing required environment variables for Coinbase live webhook tests"
)

class WebhookTestServer:
    """Test server to receive live webhooks."""
    
    def __init__(self, host: str = 'localhost', port: int = 5050) -> None:
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
def coinbase_verifier() -> CoinbaseVerifier:
    """Create a CoinbaseVerifier instance for testing."""
    return CoinbaseVerifier()

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
def coinbase_webhook(mock_forwarder: Forwarder) -> CoinbaseWebhook[ItemType]:
    """Create a CoinbaseWebhook instance for testing."""
    return CoinbaseWebhook[ItemType](forwarder=mock_forwarder)

@pytest.fixture
def test_charge_data() -> Dict[str, Any]:
    """Sample charge data for testing."""
    return {
        "name": "Live Webhook Test Product",
        "description": "Product for live webhook testing",
        "pricing_type": "fixed_price",
        "local_price": {
            "amount": "0.50",  # Small amount for testing
            "currency": "USD"
        },
        "metadata": {
            "user_id": "live_webhook_test_user",
            "product_id": "live_webhook_test_product"
        }
    }

@pytest.mark.live
@pytest.mark.regression
class TestCoinbaseLiveWebhook:
    """Live webhook regression tests for Coinbase payment verification."""

    def test_webhook_registration(self, coinbase_verifier: CoinbaseVerifier) -> None:
        """Test registering a webhook endpoint with Coinbase."""
        # Get webhook URL from environment
        webhook_url = os.getenv('COINBASE_WEBHOOK_URL')
        assert webhook_url is not None
        
        # Register webhook with Coinbase Commerce API
        headers = {
            'X-CC-Api-Key': os.getenv('COINBASE_API_KEY'),
            'X-CC-Version': '2018-03-22',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(
            'https://api.commerce.coinbase.com/webhooks',
            headers=headers,
            json={'url': webhook_url}
        )
        
        assert response.status_code in [200, 201]
        webhook_id = response.json()['data']['id']
        assert webhook_id is not None

    def test_live_charge_webhook(
        self, 
        webhook_server: WebhookTestServer,
        coinbase_verifier: CoinbaseVerifier,
        test_charge_data: Dict[str, Any]
    ) -> None:
        """Test receiving a live webhook for charge events."""
        # Create a new charge
        charge = coinbase_verifier.create_charge(test_charge_data)
        assert charge is not None
        charge_code = charge['code']
        
        # Wait for webhook (timeout after 30 seconds)
        timeout = time.time() + 30
        received_charge_webhook = False
        
        while time.time() < timeout and not received_charge_webhook:
            for webhook in webhook_server.received_webhooks:
                if (
                    webhook.get('event', {}).get('type') == 'charge:created' and
                    webhook.get('event', {}).get('data', {}).get('code') == charge_code
                ):
                    received_charge_webhook = True
                    break
            if not received_charge_webhook:
                time.sleep(1)
        
        assert received_charge_webhook, "Did not receive webhook for charge creation"

    def test_live_webhook_signature(
        self,
        webhook_server: WebhookTestServer,
        coinbase_verifier: CoinbaseVerifier,
        test_charge_data: Dict[str, Any]
    ) -> None:
        """Test verifying signatures of live webhooks."""
        # Create a new charge to trigger a webhook
        charge = coinbase_verifier.create_charge(test_charge_data)
        assert charge is not None
        
        # Wait for webhook (timeout after 30 seconds)
        timeout = time.time() + 30
        valid_signature = False
        
        while time.time() < timeout and not valid_signature:
            for webhook in webhook_server.received_webhooks:
                # Get the signature from the webhook headers
                if 'X-CC-Webhook-Signature' in request.headers:
                    signature = request.headers['X-CC-Webhook-Signature']
                    try:
                        valid_signature = coinbase_verifier.verify_signature(webhook, signature)
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
        coinbase_webhook: CoinbaseWebhook[ItemType],
        mock_forwarder: Forwarder,
        test_charge_data: Dict[str, Any]
    ) -> None:
        """Test processing of live webhooks."""
        # Create a new charge
        verifier = CoinbaseVerifier()
        charge = verifier.create_charge(test_charge_data)
        assert charge is not None
        charge_code = charge['code']
        
        # Wait for webhook and process it (timeout after 30 seconds)
        timeout = time.time() + 30
        processed_webhook = False
        
        while time.time() < timeout and not processed_webhook:
            for webhook_data in webhook_server.received_webhooks:
                if webhook_data.get('event', {}).get('data', {}).get('code') == charge_code:
                    # Process the webhook
                    try:
                        webhook_result = coinbase_webhook.parse_event_data(json.dumps(webhook_data))
                        assert webhook_result is not None
                        assert webhook_result['transaction_id'] == charge_code
                        assert webhook_result['user_id'] == test_charge_data['metadata']['user_id']
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
        coinbase_webhook: CoinbaseWebhook[ItemType],
        test_charge_data: Dict[str, Any]
    ) -> None:
        """Test webhook status transitions in live environment."""
        # Create a new charge
        verifier = CoinbaseVerifier()
        charge = verifier.create_charge(test_charge_data)
        assert charge is not None
        charge_code = charge['code']
        
        # Track status transitions
        received_statuses = set()
        timeout = time.time() + 30
        
        while time.time() < timeout and len(received_statuses) < 2:  # Wait for at least 2 different statuses
            for webhook_data in webhook_server.received_webhooks:
                if webhook_data.get('event', {}).get('data', {}).get('code') == charge_code:
                    try:
                        webhook_result = coinbase_webhook.parse_event_data(json.dumps(webhook_data))
                        if webhook_result and webhook_result['status']:
                            received_statuses.add(webhook_result['status'])
                    except Exception:
                        continue
            if len(received_statuses) < 2:
                time.sleep(1)
        
        assert len(received_statuses) >= 2, "Did not receive multiple status transitions"
        assert 'webhook_recieved' in received_statuses, "Missing initial webhook_received status" 