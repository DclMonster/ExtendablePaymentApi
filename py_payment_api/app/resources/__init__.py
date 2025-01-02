from .webhook.coinbase import CoinbaseWebhook
from .webhook.apple import AppleWebhook
from .webhook.google import GoogleWebhook
from .webhook.coinsub import CoinSubWebhook
from .webhook.paypal import PaypalWebhook
from ..services import construct_store_service
from .creditor.credit_purchase import PaymentFulfillment
from ..services import init_services
from types import TypeVar
from ..services import Services
from enum import StrEnum
ITEM_CATEGORY = TypeVar('ITEM_CATEGORY', bound=StrEnum)


_services : Services[ITEM_CATEGORY] | None = None
def init_resources() -> Services[ITEM_CATEGORY]:
    global _services
    if _services is None:
        _services = init_services()
    else:
        raise Exception("Services already initialized")
    return _services

__all__ = [
    'init_resources'
] 
