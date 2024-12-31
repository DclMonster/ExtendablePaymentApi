import requests
from flask import request
from flask_restful import Resource
from app.verifiers.verifiers import paypal_verifier

class PayPalWebhook(Resource):
    """
    Resource class to handle PayPal webhook events.
    """

    def post(self):
        """
        Handles POST requests for PayPal webhooks.
        """
        data = request.get_json()
        signature = request.headers.get('X-PayPal-Auth-Assertion')
        if not signature:
            return {'status': 'error', 'message': 'Signature not provided'}, 400
        if not paypal_verifier.verify_signature(data, signature):
            return {'status': 'error', 'message': 'Signature verification failed'}, 400
        if not data:
            return {'status': 'error', 'message': 'No event data provided'}, 400
        self.process_event(data)
        return {'status': 'success'}, 200

    def process_event(self, event_data: dict):
        """
        Processes the PayPal event data and executes registered actions.

        Parameters
        ----------
        event_data : dict
            The event data received from PayPal.
        """
        print("Received PayPal event:", event_data)
        event_type = event_data.get('event_type')

        if event_type == 'PAYMENT.SALE.COMPLETED':
            self.handle_payment_completed(event_data)
        elif event_type == 'PAYMENT.SALE.DENIED':
            self.handle_payment_denied(event_data)
        # Add more event types as needed

    def handle_payment_completed(self, event_data: dict):
        """
        Handles payment completed events.

        Parameters
        ----------
        event_data : dict
            The event data for the payment completion.
        """
        print("Payment completed:", event_data)
        # Implement logic to handle payment completion

    def handle_payment_denied(self, event_data: dict):
        """
        Handles payment denied events.

        Parameters
        ----------
        event_data : dict
            The event data for the payment denial.
        """
        print("Payment denied:", event_data)
        # Implement logic to handle payment denial

# Function to create a PayPal payment

def create_paypal_payment(amount: float, currency: str, description: str):
    """
    Creates a payment using the PayPal API.

    Parameters
    ----------
    amount : float
        The amount for the payment.
    currency : str
        The currency for the payment.
    description : str
        A description of the payment.

    Returns
    -------
    dict
        The response from the PayPal API.
    """
    url = "https://api.paypal.com/v1/payments/payment"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer YOUR_ACCESS_TOKEN"
    }
    data = {
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"
        },
        "transactions": [{
            "amount": {
                "total": f"{amount:.2f}",
                "currency": currency
            },
            "description": description
        }],
        "redirect_urls": {
            "return_url": "https://yourapp.com/return",
            "cancel_url": "https://yourapp.com/cancel"
        }
    }
    response = requests.post(url, json=data, headers=headers)
    return response.json()
