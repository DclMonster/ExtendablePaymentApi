from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Dict, List
from .available_item import AvailableItem
from .base_payment_data import BasePaymentData
T = TypeVar('T', bound=BasePaymentData)

class PaymentHandler(Generic[T], ABC):
    @abstractmethod
    def onPayment(self, payment: T):
        pass

    @abstractmethod
    def get_items(self) -> Dict[str, List[AvailableItem]]:
        pass


