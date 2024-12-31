from payment_api.app.services.subscription.abstract.subscription_serrvice import SubscriptionService, BaseSubscriptionData
class CoinSubScriptionData(BaseSubscriptionData):
    pass
class CoinsubSubscriptionService(SubscriptionService[CoinSubScriptionData]):
    def __init__(self) -> None:
        super().__init__(
            provider='coinsub',
            collection_name='coinsub_subscriptions'
        )

