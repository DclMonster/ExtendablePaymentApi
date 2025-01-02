from flask_restful import Resource, reqparse
from flask import request
from payment_api.app.services.apple_subscription_service import apple_subscription_service as provider_subscription_service
from payment_api.app.enums import PaymentProvider
from payment_api.app.verifiers import apple_verifier
from payment_api.app.services import payment_service
from payment_api.app.services.apple_subscription_service import AppleSubscriptionData
from payment_api.app.services.payment_service import AppleData
from typing import Dict, Any

webhook_args = reqparse.RequestParser()
webhook_args.add_argument('signedPayload', type=str, required=True, help='The signed payload from Apple')


class AppleWebhook(Resource):
    """
    Resource class to handle Apple webhook events.
    """

    def post(self):
        """
        Handles POST requests for Apple webhooks. Verifies the signature and processes the event data.
        """
        event_data = webhook_args.parse_args()

        jws = event_data['signedPayload']

        if not apple_verifier.verify_signature(jws):
            return {'status': 'error', 'message': 'Invalid signature'}, 400

        is_one_time_payment = payment_service.get_items().get(PaymentProvider.APPLE.value) is not None

        self.process_event(event_data, is_one_time_payment)
        return {'status': 'success'}, 200

    

    def process_event(self, event_data: dict, is_one_time_payment: bool):
        """
        Processes the Apple event data and executes registered actions.

        Parameters
        ----------
        event_data : dict
            The event data received from Apple.
        """
        print("Received Apple event:", event_data)
        parsed_data = self.parse_event_data(event_data)
        if is_one_time_payment:
            payment_service.on_apple_payment(AppleData(
                transaction_id=parsed_data.get('transaction_id') if parsed_data.get('transaction_id') is not None else "",
                amount=parsed_data.get('amount') if parsed_data.get('amount') is not None else 0.0,
                currency=parsed_data.get('currency') if parsed_data.get('currency') is not None else "",
                status=parsed_data.get('status') if parsed_data.get('status') is not None else ""
            ))
        else:
            provider_subscription_service.add_subscription(
                subscription=AppleSubscriptionData(
                    provider=PaymentProvider.APPLE.value,
                    user_id=parsed_data.get('user_id') if parsed_data.get('user_id') is not None else "",
                    subscription_data=parsed_data
                )
            )

    def parse_event_data(self, event_data: dict) -> Dict[str, Any]:
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