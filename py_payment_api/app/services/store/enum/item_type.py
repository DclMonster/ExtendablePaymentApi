from enum import StrEnum

class ItemType(StrEnum):
    SUBSCRIPTION = 'subscription'
    ONE_TIME_PAYMENT = 'one_time_payment'
    UNKNOWN = 'unknown'

