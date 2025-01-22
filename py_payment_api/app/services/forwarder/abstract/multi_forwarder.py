from typing import Dict, TypeVar, Generic, Any, Mapping, final
from .forwarder import Forwarder, PurchaseStatus
from enum import StrEnum
from abc import abstractmethod

T = TypeVar('T', bound=StrEnum)

class MultiForwarder(Forwarder, Generic[T]):
    def __init__(self, forwarders: Mapping[T, Forwarder]):
        self.forwarders = forwarders


    def forward_event(self, event_data: Dict[str, Any]) -> None:
        forwarder = self.forwarders[self._get_api_type(event_data)]
        forwarder.forward_event(event_data)

    @abstractmethod
    def _get_api_type(self, event_data: Dict[str, Any]) -> T:
        pass