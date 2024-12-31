from payment_api.app.services.subscription.abstract.subscription_serrvice import SubscriptionService, BaseSubscriptionData
class PaypalSubscriptionData(BaseSubscriptionData):
    pass
class PaypalSubscriptionService(SubscriptionService[PaypalSubscriptionData]):
    def __init__(self) -> None:
        super().__init__(
            provider='paypal',
            collection_name='paypal_subscriptions'
        )

