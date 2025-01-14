from enum import StrEnum

class PaymentProvider(StrEnum):
    APPLE = "apple"
    GOOGLE = "google"
    PAYPAL = "paypal"
    COINBASE = "coinbase"
    COINSUB = "coinsub"