from typing import TypedDict, Literal, TypeVar, Generic
from enum import StrEnum

ITEM_CATEGORY = TypeVar("ITEM_CATEGORY", bound=StrEnum)

class BasePaymentData(TypedDict, Generic[ITEM_CATEGORY]):
    purchase_id: str
    user_id: str
    item_name: str
    time_bought: str
    status: Literal["webhook_recieved", "sent_to_websocket", "sent_to_processor", "paid"]
    item_category: ITEM_CATEGORY


