from flask_restful import Resource
from flask import request
from ..services.services import apple_subscription_service as provider_subscription_service
from ..enums import PaymentProvider
from ..verifiers import apple_verifier

class AppleWebhook(Resource):
    """
    Resource class to handle Apple webhook events.
    """

    def post(self):
        """
        Handles POST requests for Apple webhooks. Verifies the signature and processes the event data.
        """
        event_data = request.json
        if not event_data:
            return {'status': 'error', 'message': 'No event data provided'}, 400
        jws = event_data.get('signedPayload')

        if not apple_verifier.verify_signature(jws):
            return {'status': 'error', 'message': 'Invalid signature'}, 400

        self.process_event(event_data)
        return {'status': 'success'}, 200

    def process_event(self, event_data: dict):
        """
        Processes the Apple event data and executes registered actions.

        Parameters
        ----------
        event_data : dict
            The event data received from Apple.
        """
        print("Received Apple event:", event_data)
        parsed_data = self.parse_event_data(event_data)
        provider_subscription_service.execute_actions(PaymentProvider.APPLE, parsed_data)

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
            'transaction_id': event_data.get('transactionId'),
            'amount': event_data.get('amount'),
            'currency': event_data.get('currency'),
            'status': event_data.get('status'),
        }
        return parsed_data 