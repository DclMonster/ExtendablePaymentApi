from flask_restful import Resource
from flask import request, jsonify
from ..services import payment_service, coinbase_subscription_service
from ..enums import PaymentProvider
from ..verifiers import coinbase_verifier
import requests

class CoinbaseWebhook(Resource):
    """
    Resource class to handle Coinbase webhook events.
    """

    def __init__(self):
        self.subscription_service = coinbase_subscription_service

    def post(self):
        """
        Handles POST requests for Coinbase webhooks. Verifies the signature and processes the event data.
        """
        data = request.get_data(as_text=True)
        signature = request.headers.get('X-Cc-Webhook-Signature', '')

        if not coinbase_verifier.verify_signature(data, signature):
            return {'status': 'error', 'message': 'Invalid signature'}, 400

        event_data = request.json
        if not event_data:
            return {'status': 'error', 'message': 'No event data provided'}, 400
        self.process_event(event_data)
        return {'status': 'success'}, 200

    def process_event(self, event_data: dict):
        """
        Processes the Coinbase event data and executes registered actions.

        Parameters
        ----------
        event_data : dict
            The event data received from Coinbase.
        """
        print("Received Coinbase event:", event_data)
        event_type = event_data.get('type')
        signature = request.headers.get('X-Coinbase-Signature')
        if not signature:
            return {'status': 'error', 'message': 'Signature not provided'}, 400
        if not coinbase_verifier.verify_signature(event_data, signature):
            return {'status': 'error', 'message': 'Signature verification failed'}, 400
        if event_type == 'charge:created':
            self.handle_charge_created(event_data)
        elif event_type == 'charge:confirmed':
            self.handle_charge_confirmed(event_data)
        elif event_type == 'charge:failed':
            self.handle_charge_failed(event_data)
        else:
            parsed_data = self.parse_event_data(event_data)
            payment_service.execute_actions(PaymentProvider.COINBASE, parsed_data)

    def handle_subscription_created(self, event_data: dict):
        """
        Handles subscription creation events.

        Parameters
        ----------
        event_data : dict
            The event data for the subscription creation.
        """
        user_id = event_data.get('user_id')
        subscription_data = event_data.get('subscription_data', {})
        self.subscription_service.add_subscription(PaymentProvider.COINBASE, user_id, subscription_data)

    def handle_subscription_canceled(self, event_data: dict):
        """
        Handles subscription cancellation events.

        Parameters
        ----------
        event_data : dict
            The event data for the subscription cancellation.
        """
        user_id = event_data.get('user_id')
        # Implement logic to handle subscription cancellation

    def parse_event_data(self, event_data: dict) -> dict:
        """
        Parses the event data to extract relevant information.

        Parameters
        ----------
        event_data : dict
            The raw event data.

        Returns
        -------
        dict
            Parsed event data with relevant fields.
        """
        parsed_data = {
            'transaction_id': event_data.get('id'),
            'amount': event_data.get('amount', {}).get('amount'),
            'currency': event_data.get('amount', {}).get('currency'),
            'status': event_data.get('status'),
        }
        return parsed_data 

    def handle_charge_created(self, event_data: dict):
        """
        Handles charge creation events.

        Parameters
        ----------
        event_data : dict
            The event data for the charge creation.
        """
        print("Charge created:", event_data)
        # Implement logic to handle charge creation

    def handle_charge_confirmed(self, event_data: dict):
        """
        Handles charge confirmation events.

        Parameters
        ----------
        event_data : dict
            The event data for the charge confirmation.
        """
        print("Charge confirmed:", event_data)
        # Implement logic to handle charge confirmation

    def handle_charge_failed(self, event_data: dict):
        """
        Handles charge failure events.

        Parameters
        ----------
        event_data : dict
            The event data for the charge failure.
        """
        print("Charge failed:", event_data)
        # Implement logic to handle charge failure 