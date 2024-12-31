from payment_api.app.services.subscription.handlers.subscription_handler import SubscriptionHandler
from payment_api.app.services.subscription.abstract.subscription_serrvice import BaseSubscriptionData

class CoinSubSubscriptionHandler(SubscriptionHandler[BaseSubscriptionData]):
    def __init__(self) -> None:
        super().__init__()

    def onSubscription(self, subscription: BaseSubscriptionData):
        print("CoinSub subscription created:", subscription)
        # Implement logic for CoinSub subscription creation

    def onSubscriptionCancel(self, subscription: BaseSubscriptionData):
        print("CoinSub subscription canceled:", subscription)
        # Implement logic for CoinSub subscription cancellation

    def onSubscriptionRenewal(self, subscription: BaseSubscriptionData):
        print("CoinSub subscription renewed:", subscription)
        # Implement logic for CoinSub subscription renewal 