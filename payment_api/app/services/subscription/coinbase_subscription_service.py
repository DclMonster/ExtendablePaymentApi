from pymongo import MongoClient
import os
from typing import Callable, List
from payment_api.app.services.subscription.abstract.subscription_serrvice import SubscriptionService, BaseSubscriptionData

class CoinbaseSubscriptionData(BaseSubscriptionData):
    pass

class CoinbaseSubscriptionService(SubscriptionService[CoinbaseSubscriptionData]):
    def __init__(self) -> None:
        super().__init__(
            provider='coinbase',
            collection_name='coinbase_subscriptions'
        )

