from .abstract import PaymentHandler
from .abstract import BasePaymentData
from typing import TypeVar, Generic, List, Optional
from .abstract.item_collection_service import ItemCollectionService

T = TypeVar('T', bound=BasePaymentData)

class OneTimePaymentHandler(PaymentHandler[BasePaymentData]):

    def __init__(self, logger: Optional[List[ItemCollectionService]] = None) -> None:
        super().__init__(logger=logger)

    def onPayment(self, payment: BasePaymentData) -> None:
        return super().onPayment(payment)
