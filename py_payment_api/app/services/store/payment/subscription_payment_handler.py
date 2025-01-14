from typing import Optional, List
from .abstract import PaymentHandler, BasePaymentData
from .abstract.item_collection_service import ItemCollectionService

class SubscriptionPaymentHandler(PaymentHandler[BasePaymentData]):

    def __init__(self, logger: Optional[List[ItemCollectionService]] = None) -> None:
        super().__init__(logger=logger)
