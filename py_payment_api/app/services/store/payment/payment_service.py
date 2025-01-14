from typing import Dict, TypeVar, Generic
from ..enum import PaymentProvider, ItemType
from enum import StrEnum
from .abstract import BasePaymentData, PaymentHandler
from .abstract.item_collection_service import ItemCollectionService

ITEM_CATEGORY = TypeVar('ITEM_CATEGORY', bound=StrEnum)
class PaymentService(Generic[ITEM_CATEGORY]):
    """
    Service class for registering and executing actions based on different payment providers.
    """

    __item_type_to_category_handler : Dict[ItemType, Dict[ITEM_CATEGORY, PaymentHandler[BasePaymentData]]]


    def __init__(self, item_collection_service: ItemCollectionService) -> None:
        self.__item_type_to_category_handler = {}
        self.item_collection_service = item_collection_service

    def handle_payment(self, provider : PaymentProvider, item_type : ItemType, category : ITEM_CATEGORY, data : BasePaymentData) -> None:
        if item_type not in self.__item_type_to_category_handler:
            raise ValueError("not found")
        category_dict = self.__item_type_to_category_handler[item_type]
        if category not in category_dict:
            raise ValueError("not found")
        handler = category_dict[category]
        handler.onPayment(data)
        
        # Log or collect items after payment is handled
        self.item_collection_service.collect_items(f"Payment handled for provider: {provider}, item type: {item_type}, category: {category}")

    def register_handler(self, item_type : ItemType, category : ITEM_CATEGORY, handler : PaymentHandler[BasePaymentData]) -> None:
        if item_type not in self.__item_type_to_category_handler:
            self.__item_type_to_category_handler[item_type] = {}
        category_dict = self.__item_type_to_category_handler[item_type]
        if category in category_dict:
            raise ValueError("handler already set")
        category_dict[category] = handler