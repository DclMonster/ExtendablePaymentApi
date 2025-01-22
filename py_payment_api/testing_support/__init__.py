"""Testing support package."""
from ..app.services.store import PaymentProvider
from typing import List

ENABLED_PROVIDERS: List[PaymentProvider] = [
    PaymentProvider.COINBASE,
    PaymentProvider.APPLE,
    PaymentProvider.GOOGLE,
    PaymentProvider.PAYPAL,
    PaymentProvider.COINSUB
]

__all__ = ['ENABLED_PROVIDERS'] 