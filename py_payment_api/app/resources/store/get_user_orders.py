from flask_restful import Resource, reqparse # type: ignore
from ...services.store.payment.abstract.item_collection_service import ItemCollectionService
from typing import Tuple, TypeVar, Dict, Any
from enum import StrEnum
from ...services import get_services

T = TypeVar('T', bound=StrEnum)

get_args = reqparse.RequestParser()
get_args.add_argument("user_id", type=str, required=True, help="User ID is required")

class GetUserOrders(Resource):


    def get(self) -> Tuple[Dict[str, Any], int]:
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
        args = get_args.parse_args()
        user_id = args['user_id']
        orders = get_services().get_orders_by_user_id(user_id)
        return {'orders': orders}, 200