from flask_restful import Resource
from ..services import payment_service, apple_subscription_service, coinbase_subscription_service, google_subscription_service

class StoreItems(Resource):
    """
    Resource class to handle store item retrieval.
    """

    def get(self):
        """
        Handles GET requests to retrieve store items.

        Returns
        -------
        dict
            A dictionary containing the list of store items.
        """
        
        result = {}
        result["items"] = payment_service.get_items()
        result["subscriptions"] = {
            "apple": apple_subscription_service.get_items(),
            "coinbase": coinbase_subscription_service.get_items(),
            "google": google_subscription_service.get_items()
        }
        return result, 200