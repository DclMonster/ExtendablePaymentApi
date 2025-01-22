from .abstract.single_forwarder import SingleForwarder
import os
import requests
from typing import Optional, List, Generic, TypeVar, Dict, Any, final
from ..store.payment.abstract.item_collection_service import ItemCollectionService, PurchaseStatus
from enum import StrEnum
SUBSCRIPTION_ITEM_CATEGORY = TypeVar('SUBSCRIPTION_ITEM_CATEGORY', bound=StrEnum)
ONE_TIME_ITEM_CATEGORY = TypeVar('ONE_TIME_ITEM_CATEGORY', bound=StrEnum)
class ForwarderError(Exception):
    pass

@final
class RestfulForwarder(SingleForwarder):

    def __init__(self, url: str) -> None:
        super().__init__(PurchaseStatus.SENT_TO_PROCESSOR)
        self.url = url
        self.route = os.getenv('ROUTE', "/creditor_api")

    @final
    def _on_forward_event(self, event_data: Dict[str, Any]) -> None:
        full_url = f"{self.url}{self.route}"
        try:
            response = requests.post(full_url, json=event_data, headers={"Content-Type": "application/json"})
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise ForwarderError(f"Failed to forward event to {full_url}: {e}") from e