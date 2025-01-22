from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List, Optional, final, Type, Any, ClassVar
from .base_payment_data import BasePaymentData
from .item_collection_service import ItemCollectionService
from enum import StrEnum
from .item_collection_service import PurchaseStatus

class PaymentException(Exception):
    """Exception raised for payment errors."""
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)

ITEM_CATEGORY = TypeVar("ITEM_CATEGORY", bound=StrEnum)
T = TypeVar("T", bound=BasePaymentData[Any])
class PaymentHandler(Generic[ITEM_CATEGORY, T], ABC):

    def __init__(self, category: ITEM_CATEGORY, logger: Optional[ItemCollectionService[ITEM_CATEGORY]] = None) -> None:
        self.__logger = logger
        self.__category: ITEM_CATEGORY = category

    @final
    def payment(self, payment: T) -> bool:
        try:
            self.onPayment(payment)
            if self.__logger:
                self.__logger.change_order_status(payment["purchase_id"], PurchaseStatus.PAID)
            return True
        except Exception:
            raise PaymentException("Crediting failed")

    @abstractmethod
    def onPayment(self, payment: T) -> None:
        pass

    @property
    def category(self) -> ITEM_CATEGORY:
        return self.__category



