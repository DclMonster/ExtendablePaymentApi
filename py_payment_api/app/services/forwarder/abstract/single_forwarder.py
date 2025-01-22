from typing import Dict, Any, final
from abc import ABC, abstractmethod
from .forwarder import Forwarder
from ....services import Services, PurchaseStatus, get_services

class SingleForwarder(Forwarder):

    def __init__(self, status: PurchaseStatus) -> None:
        self._service :Services[Any, Any] = get_services()
        self.__status = status

 
    @final
    def forward_event(self, event_data: Dict[str, Any]) -> None:
        """
        Forward the event data.
        """
        order_id = str(event_data.get('order_id', ''))
        if self._service:
            self._service.change_order_status(order_id, self.__status)
        self._on_forward_event(event_data)

    @abstractmethod
    def _on_forward_event(self, event_data: Dict[str, Any]) -> None:
        pass