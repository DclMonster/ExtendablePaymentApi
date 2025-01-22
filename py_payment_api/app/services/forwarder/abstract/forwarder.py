from abc import ABC, abstractmethod
from typing import Dict, Any, final, TypeVar, Generic, Protocol
from ExtendablePaymentApi.py_payment_api.app.services.store.payment.abstract.item_collection_service import ItemCollectionService, PurchaseStatus
from enum import StrEnum
from ....services import get_services, Services

class ForwarderType(StrEnum):
    WEBSOCKET = "websocket"
    REST = "rest"

class Forwarder(Protocol):

    @abstractmethod
    def forward_event(self, event_data: Dict[str, Any]) -> None:
        pass
