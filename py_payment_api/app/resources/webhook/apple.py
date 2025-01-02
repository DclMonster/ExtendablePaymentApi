from flask_restful import Resource, reqparse
from flask import request
from payment_api.app.services.apple_subscription_service import apple_subscription_service as provider_subscription_service
from payment_api.app.enums import PaymentProvider
from payment_api.app.verifiers import apple_verifier
from payment_api.app.services import payment_service
from payment_api.app.services.apple_subscription_service import AppleSubscriptionData
from payment_api.app.services.payment_service import AppleData
from typing import Dict, Any
from payment_api.app.resources.webhook.abstract.abstract_webhook import AbstractWebhook

webhook_args = reqparse.RequestParser()
webhook_args.add_argument('signedPayload', type=str, required=True, help='The signed payload from Apple')


def verify_apple_signature(jws: str) -> bool:
    """
    Verify the signature of the Apple webhook event.

    Parameters
    ----------
    jws : str
        The signed payload from Apple.

    Returns
    -------
    bool
        True if the signature is valid, False otherwise.
    """
    return apple_verifier.verify_signature(jws)


def process_apple_event(event_data: dict, is_one_time_payment: bool):
    """
    Process the Apple event data and execute registered actions.

    Parameters
    ----------
    event_data : dict
        The event data received from Apple.
    is_one_time_payment : bool
        Indicates if the event is a one-time payment.
    """
    print("Received Apple event:", event_data)
    parsed_data = parse_apple_event_data(event_data)
    if is_one_time_payment:
        payment_service.on_apple_payment(AppleData(
            transaction_id=parsed_data.get('transaction_id', ""),
            amount=parsed_data.get('amount', 0.0),
            currency=parsed_data.get('currency', ""),
            status=parsed_data.get('status', "")
        ))
    else:
        provider_subscription_service.add_subscription(
            subscription=AppleSubscriptionData(
                provider=PaymentProvider.APPLE.value,
                user_id=parsed_data.get('user_id', ""),
                subscription_data=parsed_data
            )
        )


def parse_apple_event_data(event_data: dict) -> Dict[str, Any]:
    """
    Parse the Apple event data to extract relevant information.

    Parameters
    ----------
    event_data : dict
        The raw event data.

    Returns
    -------
    dict
        Parsed event data with relevant fields.
    """
    return {
        'transaction_id': event_data.get('transactionId'),
        'amount': event_data.get('amount'),
        'currency': event_data.get('currency'),
        'status': event_data.get('status'),
    }


class AppleWebhook(AbstractWebhook, Resource):
    """
    Resource class to handle Apple webhook events.
    """

    def __init__(self):
        super().__init__(apple_verifier.verify_signature)

    def is_one_time_payment(self) -> bool:
        """
        Determine if the Apple event is a one-time payment.

        Returns
        -------
        bool
            True if it is a one-time payment, False otherwise.
        """
        return payment_service.get_items().get(PaymentProvider.APPLE.value) is not None

    def post(self):
        """
        Handles POST requests for Apple webhooks. Verifies the signature and processes the event data.
        """
        event_data = webhook_args.parse_args()

        jws = event_data['signedPayload']

        if not verify_apple_signature(jws):
            return {'status': 'error', 'message': 'Invalid signature'}, 400

        is_one_time_payment = self.is_one_time_payment()

        process_apple_event(event_data, is_one_time_payment)
        return {'status': 'success'}, 200 