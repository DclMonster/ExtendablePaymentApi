from flask_restful import Resource, reqparse # type: ignore
from ...services.store.payment.abstract.item_collection_service import ItemCollectionService
class GetUserOrders(Resource):
    def __init__(self, item_collection_service: ItemCollectionService):
        self.item_collection_service = item_collection_service

    def get(self, user_id: str):
        """
        Retrieves the order status of all orders for a given user ID.

        Parameters
        ----------
        user_id : str
            The ID of the user whose orders are to be retrieved.

        Returns
        -------
        dict
            A dictionary containing the order statuses.
        """
        orders = self.item_collection_service.get_orders_by_user_id(user_id)
        return {'orders': orders}, 200