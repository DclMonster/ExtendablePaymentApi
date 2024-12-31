from abc import ABC, abstractmethod
from typing import TypeVar, Generic
from payment_api.app.services.subscription.abstract.subscription_serrvice import BaseSubscriptionData

T = TypeVar('T', bound=BaseSubscriptionData)

class SubscriptionHandler(ABC, Generic[T]):
    
    @abstractmethod
    def onSubscription(self, subscription: T):
        pass

    @abstractmethod
    def onSubscriptionCancel(self, subscription: T):
        pass

    @abstractmethod
    def onSubscriptionRenewal(self, subscription: T):
        pass

