from pymongo import MongoClient
import os
from typing import Callable, List
from payment_api.app.services.subscription.abstract.subscription_serrvice import SubscriptionService, BaseSubscriptionData

class GoogleSubscriptionData(BaseSubscriptionData):
    pass

class GoogleSubscriptionService(SubscriptionService[GoogleSubscriptionData]):
    def __init__(self) -> None:
        super().__init__(
            provider='google',
            collection_name='google_subscriptions'
        )

