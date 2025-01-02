from enum import Enum

class StrEnum(str, Enum):
    pass

class PaymentProvider(StrEnum):
    COINBASE = "coinbase"
    APPLE = "apple"
    GOOGLE = "google" 
    PAYPAL = "paypal"
    COINSUB = "coinsub"
