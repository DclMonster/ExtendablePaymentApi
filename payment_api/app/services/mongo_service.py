from pymongo import MongoClient
import os

class MongoService:
    """
    Service class for interacting with MongoDB to retrieve store items.
    """

    def __init__(self):
        """
        Initializes the MongoDB client and selects the database and collection.
        """
        mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
        self.client = MongoClient(mongo_uri)
        self.db = self.client['store_db']  # Replace 'store_db' with your database name
        self.collection = self.db['items']  # Replace 'items' with your collection name

    def get_items(self):
        """
        Retrieves all items from the store collection.

        Returns
        -------
        list
            A list of items from the store.
        """
        return list(self.collection.find({})) 