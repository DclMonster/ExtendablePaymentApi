from abc import ABC, abstractmethod
from typing import Callable
from ExtendablePaymentApi.py_payment_api.app.services.store.payment.abstract.item_collection_service import ItemCollectionService
class Forwarder(ABC):

    __logging_function : Callable[[Logger], None]
    def __init__(self, logging_function : Callable[[Logger], None]) -> None:
        self.__logging_function = logging_function

    @final
    def forward_event(self, event_data: dict) -> None:
        """
        Forward the event data.
        """
        self.__logging_function(logger)
        self._on_forward_event(event_data)

    @abstractmethod
    def _on_forward_event(self, event_data: dict) -> None:
        pass