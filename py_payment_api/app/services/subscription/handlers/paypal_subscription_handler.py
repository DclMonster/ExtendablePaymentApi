from payment_api.app.services.subscription.handlers.subscription_handler import SubscriptionHandler
from payment_api.app.services.subscription.abstract.subscription_serrvice import BaseSubscriptionData

class PayPalSubscriptionHandler(SubscriptionHandler[BaseSubscriptionData]):
    def __init__(self) -> None:
        super().__init__()

    def onSubscription(self, subscription: BaseSubscriptionData):
        print("PayPal subscription created:", subscription)
        # Implement logic for PayPal subscription creation

    def onSubscriptionCancel(self, subscription: BaseSubscriptionData):
        print("PayPal subscription canceled:", subscription)
        # Implement logic for PayPal subscription cancellation

    def onSubscriptionRenewal(self, subscription: BaseSubscriptionData):
        print("PayPal subscription renewed:", subscription)
        # Implement logic for PayPal subscription renewal 