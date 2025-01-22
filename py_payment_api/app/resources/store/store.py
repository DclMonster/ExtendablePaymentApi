from flask_restful import Resource
from typing import Dict, Any, Tuple
from ...services import Services, get_services

class StoreItems(Resource):
    """
    Resource class to handle store item retrieval.
    """

    def get(self) -> Tuple[Dict[str, Any], int]:
        """
        Handles GET requests to retrieve store items.

        Returns
        -------
        dict
            A dictionary containing the list of store items.
        """
        
        result = {}
        services : Services[Any, Any] = get_services()
        result["items"] = services.get_all_items()
        return result, 200