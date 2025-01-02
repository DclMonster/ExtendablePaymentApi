from payment_api.app.services.subscription.handlers.subscription_handler import SubscriptionHandler
from payment_api.app.services.subscription.abstract.subscription_serrvice import BaseSubscriptionData

class TierSubscriptionHandler(SubscriptionHandler[BaseSubscriptionData]):
    def __init__(self) -> None:
        super().__init__()

    def onSubscription(self, subscription: BaseSubscriptionData):
        pass

    def onSubscriptionCancel(self, subscription: BaseSubscriptionData):
        pass

    def onSubscriptionRenewal(self, subscription: BaseSubscriptionData):
        pass
wwwww