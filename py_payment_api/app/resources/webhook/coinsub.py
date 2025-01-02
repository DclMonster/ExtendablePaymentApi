from flask_restful import Resource
from flask import request
import requests
from payment_api.app.verifiers.coinsub_verifier import coinsub_verifier
class CoinSubWebhook(Resource):
    """
    Resource class to handle CoinSub webhook events.
    """

    def post(self):
        """
        Handles POST requests for CoinSub webhooks.
        """
        data = request.get_json()
        if not data:
            return {'status': 'error', 'message': 'No event data provided'}, 400
        self.process_event(data)
        return {'status': 'success'}, 200

    def process_event(self, event_data: dict):
        """
        Processes the CoinSub event data and executes registered actions.

        Parameters
        ----------
        event_data : dict
            The event data received from CoinSub.
        """
        signature = request.headers.get('X-Coinsub-Signature')
        print("Received CoinSub event:", event_data)
        event_type = event_data.get('event_type')
        if not coinsub_verifier.verify_signature(event_data, signature):
            return {'status': 'error', 'message': 'Signature verification failed'}, 400
        if event_type == 'subscription_created':
            self.handle_subscription_created(event_data)
        elif event_type == 'subscription_canceled':
            self.handle_subscription_canceled(event_data)
        # Add more event types as needed

    def handle_subscription_created(self, event_data: dict):
        """
        Handles subscription creation events.

        Parameters
        ----------
        event_data : dict
            The event data for the subscription creation.
        """
        print("Subscription created:", event_data)
        # Implement logic to handle subscription creation

    def handle_subscription_canceled(self, event_data: dict):
        """
        Handles subscription cancellation events.

        Parameters
        ----------
        event_data : dict
            The event data for the subscription cancellation.
        """
        print("Subscription canceled:", event_data)
        # Implement logic to handle subscription cancellation

# Function to create a CoinSub subscription

def create_coinsub_subscription(user_id: str, plan_id: str):
    """
    Creates a subscription using the CoinSub API.

    Parameters
    ----------
    user_id : str
        The ID of the user.
    plan_id : str
        The ID of the subscription plan.

    Returns
    -------
    dict
        The response from the CoinSub API.
    """
    url = "https://api.coinsub.com/v1/subscriptions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer YOUR_ACCESS_TOKEN"
    }
    data = {
        "user_id": user_id,
        "plan_id": plan_id
    }
    response = requests.post(url, json=data, headers=headers)
    return response.json() 