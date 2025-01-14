from typing import Dict, TypeVar, Generic
from .forwarder import Forwarder
from enum import StrEnum

T = TypeVar('T', bound=StrEnum)

class MultiForwarder(Generic[T], Forwarder):
    def __init__(self, forwarders: Dict[T, Forwarder]):
        self.forwarders = forwarders

    def _on_forward_event(self, event_data: dict) -> None:
        api_type = event_data.get('api_type')
        if not api_type or api_type not in self.forwarders:
            raise ValueError("Invalid or missing API type")
        
        forwarder = self.forwarders[api_type]
        forwarder.forward_event(event_data)
