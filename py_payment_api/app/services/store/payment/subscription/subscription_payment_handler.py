from typing import Optional, List, Generic, TypeVar, Any
from enum import StrEnum
from ..abstract import PaymentHandler, BasePaymentData
from ..abstract.item_collection_service import ItemCollectionService
from ....store.enum import ItemType
from .subscription_payment_data import SubscriptionPaymentData

ITEM_CATEGORY = TypeVar("ITEM_CATEGORY", bound=StrEnum)
T = TypeVar("T", bound=SubscriptionPaymentData[Any])

class SubscriptionPaymentHandler(Generic[ITEM_CATEGORY, T], PaymentHandler[ITEM_CATEGORY, T]):
    def __init__(self, category: ITEM_CATEGORY, logger: Optional[ItemCollectionService[ITEM_CATEGORY]] = None) -> None:
        super().__init__(category, logger=logger)

    def onPayment(self, payment: T) -> None:
        if payment["status"] not in ("paid", "webhook_recieved", "sent_to_websocket", "sent_to_processor"):
            raise ValueError(f"Invalid payment status: {payment['status']}")
        print(f"Payment received for {payment['item_category']} item")


