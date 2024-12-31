from typing import TypeVar, Generic, List
from abc import ABC, abstractmethod
import os
from pymongo import MongoClient
from payment_api.app.services.subscription.abstract.base_subscription_data import BaseSubscriptionData
from payment_api.app.services.subscription.handlers.subscription_handler import SubscriptionHandler

T = TypeVar('T', bound=BaseSubscriptionData)

class SubscriptionService(Generic[T], ABC):
    """
    Base service class for managing subscriptions in MongoDB and executing actions on subscription events.
    """

    def __init__(self, provider: str, collection_name: str = 'subscriptions', items_collection_name: str = 'items') -> None:
        mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
        self.client = MongoClient(mongo_uri)
        self.db = self.client['RPG']
        self.collection = self.db[collection_name]
        self.items_collection = self.db[items_collection_name]
        self.__handlers: List[SubscriptionHandler[T]] = []
        self.provider = provider

    def add_subscription(self, subscription: T) -> None:
        count = self.collection.count_documents({'user_id': subscription['user_id'], 'provider': self.provider})
        if count > 0:
            for handler in self.__handlers:
                handler.onSubscriptionRenewal(subscription)
            self.collection.update_one({'user_id': subscription['user_id'], 'provider': self.provider}, {'$set': subscription})
        else:
            self.collection.insert_one(subscription)
        self.execute_start_actions(subscription)

    def remove_subscription(self, user_id: str) -> None:
        subscription = self.collection.find_one({'user_id': user_id, 'provider': self.provider})
        if subscription:
            self.collection.delete_one({'user_id': user_id, 'provider': self.provider})
            self.execute_stop_actions(subscription)
    
    def get_subscriptions(self, user_id: str) -> List[T]:
        return list(self.collection.find({'user_id': user_id, 'provider': self.provider}))
    
    def register_handler(self, handler: SubscriptionHandler[T]) -> None:
        self.__handlers.append(handler)

    def execute_start_actions(self, subscription_data: T) -> None:
        for handler in self.__handlers:
            handler.onSubscription(subscription_data)

    def execute_stop_actions(self, subscription_data: T) -> None:
        for handler in self.__handlers:
            handler.onSubscriptionCancel(subscription_data)

    def get_items(self) -> List[T]:
        return list(self.items_collection.find())


