from ..abstract import BasePaymentData
from typing import TypeVar
from enum import StrEnum

ITEM_CATEGORY = TypeVar("ITEM_CATEGORY", bound=StrEnum)

class OneTimePaymentData(BasePaymentData[ITEM_CATEGORY]):
    quantity: int

