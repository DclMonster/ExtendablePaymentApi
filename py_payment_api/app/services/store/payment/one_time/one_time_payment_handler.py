from ..abstract import PaymentHandler
from ..abstract import BasePaymentData
from typing import TypeVar, Generic, List, Optional, Any
from ..abstract.item_collection_service import ItemCollectionService
from enum import StrEnum
from .one_time_payment_data import OneTimePaymentData
from ....store.enum import ItemType

ITEM_CATEGORY = TypeVar("ITEM_CATEGORY", bound=StrEnum)
T = TypeVar("T", bound=OneTimePaymentData[Any])
class OneTimePaymentHandler(Generic[ITEM_CATEGORY, T], PaymentHandler[ITEM_CATEGORY, T]):

    def __init__(self, category: ITEM_CATEGORY, logger: Optional[ItemCollectionService[ITEM_CATEGORY]] = None) -> None:
        super().__init__(category, logger=logger)

    def onPayment(self, payment: T) -> None:
        if payment["status"] not in ("paid", "webhook_recieved", "sent_to_websocket", "sent_to_processor"):
            raise ValueError(f"Invalid payment status: {payment['status']}")
        print(f"Payment received for {payment['item_category']} item")
    