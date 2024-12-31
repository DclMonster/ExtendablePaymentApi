from pymongo import MongoClient
import os
from typing import Callable, List
from payment_api.app.services.subscription.abstract.subscription_serrvice import SubscriptionService, BaseSubscriptionData


class AppleSubscriptionData(BaseSubscriptionData):
    pass

class AppleSubscriptionService(SubscriptionService[AppleSubscriptionData]):
    """
    Service class for managing Apple subscriptions.
    """
    def __init__(self) -> None:
        super().__init__(
            provider='apple',
            collection_name='apple_subscriptions'
        )



