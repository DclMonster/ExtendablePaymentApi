from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List, Optional, final
from .base_payment_data import BasePaymentData
from .item_collection_service import ItemCollectionService

T = TypeVar('T', bound=BasePaymentData)

class PaymentHandler(Generic[T], ABC):

    def __init__(self, logger: Optional[List[ItemCollectionService]] = None) -> None:
        super().__init__()
        self.logger = logger

    @final
    def payment(self, payment: T) -> None:
        self.onPayment(payment)
        if self.logger:
            for log_service in self.logger:
                log_service.log(payment)

    @abstractmethod
    def onPayment(self, payment: T) -> None:
        pass



