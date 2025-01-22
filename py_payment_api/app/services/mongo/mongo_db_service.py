from pymongo import MongoClient
import os
from abc import ABC, abstractmethod
from pymongo.database import Database
from typing import Any
class MongoDBService(ABC):
    """
    Service class for interacting with MongoDB to retrieve store items.
    """

    __client: MongoClient[Any]
    _db: Database[Any]

    def __init__(self, database_name: str = 'Store'):
        """
        Initializes the MongoDB client and selects the database and collection.
        """
        mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
        self.__client = MongoClient(mongo_uri)
        self._db = self.__client[database_name]
