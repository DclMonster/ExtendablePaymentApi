from flask_restful import Resource
from flask import request
from ..services.services import google_subscription_service as provider_subscription_service
from ..enums import PaymentProvider
from ..verifiers import google_verifier
from ..services.subscription.google_subscription_service import GoogleSubscriptionData

class GoogleWebhook(Resource):
    """
    Resource class to handle Google webhook events.
    """

    def post(self):
        """
        Handles POST requests for Google webhooks. Verifies the signature and processes the event data.
        """
        event_data = request.json
        if not event_data:
            return {'status': 'error', 'message': 'No event data provided'}, 400
        jwt_token = event_data.get('jwtToken')

        if not google_verifier.verify_signature(jwt_token):
            return {'status': 'error', 'message': 'Invalid signature'}, 400

        self.process_event(event_data)
        return {'status': 'success'}, 200

    def process_event(self, event_data: dict):
        """
        Processes the Google event data and executes registered actions.

        Parameters
        ----------
        event_data : dict
            The event data received from Google.
        """
        print("Received Google event:", event_data)
        signature = request.headers.get('X-Google-Auth-Assertion')
        if not signature:
            return {'status': 'error', 'message': 'Signature not provided'}, 400
        if not google_verifier.verify_signature(jwt_token, signature):
            return {'status': 'error', 'message': 'Signature verification failed'}, 400
        parsed_data = self.parse_event_data(event_data)
        provider_subscription_service.add_subscription(
            GoogleSubscriptionData(
                user_id=parsed_data.get('user_id'),
                provider=PaymentProvider.GOOGLE,
                transaction_id=parsed_data.get('transaction_id'),
                amount=parsed_data.get('amount'),
                currency=parsed_data.get('currency'),
                status=parsed_data.get('status')
            )
        )

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